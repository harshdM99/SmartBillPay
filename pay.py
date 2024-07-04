from selenium import webdriver
import os

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
load_dotenv()

BRAVE_PATH = os.getenv("BRAVE_PATH")
USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")
LOGIN_PAGE = os.getenv("LOGIN_PAGE")

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
        print(f"Timed out! Could not load {element_identifier}")
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

def navigate_to_payment_page(driver):
    credit_card = find_element_after_load(driver, By.NAME, "CCA_details")
    if credit_card:
        credit_card.click()
        make_payment_button = find_element_after_load(driver, By.ID, "makePaymentWidget")
        make_payment_button.click()
        if make_payment_button:
            return True
    return False

def make_payment(driver):
    actions = ActionChains(driver)
    
    amount_to_pay_input = find_element_after_load(driver, By.ID, "amount")
    actions.move_to_element(amount_to_pay_input).click().perform()
    
    # TODO: take this as runtime argument i.e if statement balance or current balance
    pay_statement_balance = True 
    if pay_statement_balance:
        amount_to_pay_ul = find_element_after_load(driver, By.ID, "statement-balance-link")
    else:
        amount_to_pay_ul = find_element_after_load(driver, By.ID, "current-balance-link")

    amount_to_pay_option = find_element_after_load(amount_to_pay_ul, By.TAG_NAME, "a")
    payment_button = find_element_after_load(driver, By.ID, "continue-bpPayment")
    
    if amount_to_pay_option and payment_button:
        amount_to_pay_option.click()

        try:
            amount_to_pay_str = amount_to_pay_input.get_attribute('value')
            amount_to_pay = float(amount_to_pay_str)

            if amount_to_pay <= 0.00 or amount_to_pay > 300.00:
                return False
        except ValueError:
            return False

        payment_button.click()

        # TODO: uncomment to confirm the payment
        # confirm_payment_button = find_element_after_load(driver, By.ID, "continue-bp-payment-confirm")
        # confirm_payment_button.click()

        # TODO: additional check to confirm if payment successful
        return True

def main():
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        login(driver)
        if not navigate_to_payment_page(driver):
            raise Exception
        make_payment(driver)
    except Exception as e:
        print("error: ", e)
    finally:
        if not debug_mode:
            driver.quit()

if __name__ == "__main__":
    main()