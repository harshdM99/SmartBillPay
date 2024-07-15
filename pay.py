from selenium import webdriver
import os
import logging
import io
from email.message import EmailMessage
import smtplib

from dotenv import load_dotenv
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# TODO: GitHub readme
# TODO: Docstring in functions
# TODO: make this a runtime arg
debug_mode = True

log_stream = io.StringIO()
log_format = "%(message)s"
logging.basicConfig(stream=log_stream, level=logging.INFO, format=log_format)

load_dotenv()

BRAVE_PATH = os.getenv("BRAVE_PATH")
USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")
LOGIN_PAGE = os.getenv("LOGIN_PAGE")
SENDER_EMAIL = os.getenv("SENDER_EMAIL_ID")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# get driver path
script_path = Path(__file__).resolve().parent
driver_path = script_path.joinpath("chromedriver-win64", "chromedriver.exe")

# set options
chrome_options = Options()
chrome_options.binary_location = BRAVE_PATH
if debug_mode:
    chrome_options.add_experimental_option("detach", True)
else:
    chrome_options.add_argument("--headless")

def find_element_after_load(driver, by, element_identifier, presence=True, timeout=5):
    '''
        Function to wait for either element visibility or clickability.
    '''
    try:
        if presence:
            element_present = EC.presence_of_element_located((by, element_identifier))
        else:
            element_present = EC.element_to_be_clickable((by, element_identifier))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        logging.info(f"Timed out! Could not load {element_identifier}")
        return None
    return driver.find_element(by, element_identifier)

def login(driver):
    # get website
    driver.get(LOGIN_PAGE)

    # get inputs
    user_id_input = find_element_after_load(driver, By.ID, "enterID-input")
    password_input = find_element_after_load(driver, By.ID, "tlpvt-passcode-input")

    if user_id_input and password_input:
        user_id_input.send_keys(USER_ID)
        password_input.send_keys(PASSWORD)

    submit_button = find_element_after_load(driver, By.ID, "login_button")
    if submit_button:
        submit_button.click()
        logging.info("Successfully logged in to the account!")

def navigate_to_payment_page(driver):
    actions = ActionChains(driver)

    try:
        credit_card_payment = find_element_after_load(driver, By.XPATH, "//li[@id='fsd-li-transfers']/a")

        if credit_card_payment:
            actions.move_to_element(credit_card_payment).perform()

            payment_button = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@id='bofa-credit-loan']/a[@name='onh_inside_bank_make_transfer']"))
            )

            if payment_button is None:
                logging.info("Cannot find the payment button")
                return False

            actions.move_to_element(payment_button).click().perform()
            return True
    except Exception as e:
        logging.info("Failed to navigate to payment page!\n", e)
    
    return False

def make_payment(driver):
    if not navigate_to_payment_page(driver):
        return False

    # try:
    actions = ActionChains(driver)
    open_account_input = find_element_after_load(driver, By.ID, "select-input_paymentFromAccount")
    actions.move_to_element(open_account_input).click().perform()

    choose_account_input = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@id='paymentFromAccount_select-dropdown']//span[contains(., 'Adv SafeBalance Banking')]"))
    )
    choose_account_input.click()

    choose_amt_input = find_element_after_load(driver, By.XPATH, "//fieldset[@id='creditCardAmount']//input[@id='cca_option_current_balance']")
    print(choose_amt_input)

    if choose_amt_input:
        amount_to_pay_str = find_element_after_load(driver, By.XPATH, "//label[@for='cca_option_current_balance']")
        amount_to_pay_str = amount_to_pay_str[amount_to_pay_str.find('$'):]
        amount_to_pay = float(amount_to_pay_str)
        print(amount_to_pay)

        if amount_to_pay <= 0.00:
            logging.info("No payment due!")
            return False
        if amount_to_pay > 300.00:
            logging.info("Amount more than $300.")
            # return False

        choose_amt_input.click()
        next_button = find_element_after_load(driver, By.XPATH, "//button[text()='Next']")
        next_button.click()

        confirm_button = find_element_after_load(driver, By.XPATH, "//div[@id='payment-review-confirmation-container']//button[text()='Schedule']")
        print(confirm_button)
        # confirm_button.click()
        # TODO: additional check to confirm if payment successful
    else:
        logging.info("No current balance found! Exiting..")
        return False
    # except:
        
    return True

def send_message(subject, receiver):
    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.set_content(log_stream.getvalue())

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
        smtp.send_message(msg)

def main():
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        login(driver)

        payment_status = make_payment(driver)
        if payment_status:
            message = "Payment Success!"
            logging.info(message)
        else:
            message = "Payment failed!"
            logging.info(message)
        # send_message(message, RECEIVER_EMAIL)
    except WebDriverException as e:
        logging.info("Difficulty with WebDriver : ", e)
    except smtplib.SMTPException as e:
        logging.info("Could not send email! ", e)
    finally:
        if debug_mode:
            print(log_stream.getvalue())
        else:
            driver.quit()

if __name__ == "__main__":
    main()