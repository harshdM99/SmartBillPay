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

def find_element_after_load(driver, by, element_identifier, timeout=5):
    try:
        element_present = EC.presence_of_element_located((by, element_identifier))
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
    credit_card = find_element_after_load(driver, By.NAME, "CCA_details")
    if credit_card:
        try:
            credit_card.click()
            make_payment_button = find_element_after_load(driver, By.ID, "makePaymentWidget")
            make_payment_button.click()
            if make_payment_button:
                logging.info("Successfully reached the payment page!")
                return True
            logging.info("Failed to navigate to payment page!")
            return False
        except:
            logging.info("Failed to navigate to payment page!")

    logging.info("Credit card not found!")
    return False

def make_payment(driver):
    if not navigate_to_payment_page(driver):
        return False
    
    actions = ActionChains(driver)
    amount_to_pay_input = find_element_after_load(driver, By.ID, "amount")
    actions.move_to_element(amount_to_pay_input).click().perform()
    
    # TODO: take this as runtime argument i.e if statement balance or current balance
    pay_statement_balance = False 
    if pay_statement_balance:
        logging.info("Paying statement balance")
        amount_to_pay_ul = find_element_after_load(driver, By.ID, "statement-balance-link")
    else:
        logging.info("Paying current balance")
        amount_to_pay_ul = find_element_after_load(driver, By.ID, "current-balance-link")

    amount_to_pay_option = find_element_after_load(amount_to_pay_ul, By.TAG_NAME, "a")
    payment_button = find_element_after_load(driver, By.ID, "continue-bpPayment")
    
    if amount_to_pay_option and payment_button:
        amount_to_pay_option.click()

        try:
            amount_to_pay_str = amount_to_pay_input.get_attribute('value')
            amount_to_pay = float(amount_to_pay_str)

            if amount_to_pay <= 0.00:
                logging.info("No payment due!")
                return False
            if amount_to_pay > 300.00:
                logging.info("Amount more than $300.")
                return False
        except ValueError:
            return False

        payment_button.click()
        # TODO: uncomment to confirm the payment
        confirm_payment_button = find_element_after_load(driver, By.ID, "continue-bp-payment-confirm")
        confirm_payment_button.click()

        # TODO: additional check to confirm if payment successful
        return True
    
    logging.info("Facing issues! It might be possible that no current balance has been posted to your account yet.")
    return False

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
        send_message(message, RECEIVER_EMAIL)
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