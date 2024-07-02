from selenium import webdriver
import os

from dotenv import load_dotenv
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

debug_mode = True
load_dotenv()

BRAVE_PATH = os.getenv("BRAVE_PATH")
USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")

def find_element_after_load(driver, by, element_identifier, timeout=5):
    try:
        element_present = EC.presence_of_element_located((by, element_identifier))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print(f"Timed out! Could not load {element_identifier}")
        return None
    return driver.find_element(by, element_identifier)

# create service
script_path = Path(__file__).resolve().parent
driver_path = script_path.joinpath("chromedriver-win64", "chromedriver.exe")
service = Service(driver_path)

# set options
chrome_options = Options()
chrome_options.binary_location = BRAVE_PATH
if debug_mode:
    chrome_options.add_experimental_option("detach", True)
else:
    chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=chrome_options)

# get website
driver.get("https://secure.bankofamerica.com/login/sign-in/signOnV2Screen.go")

# get inputs
user_id_input = find_element_after_load(driver, By.ID, "enterID-input")
password_input = find_element_after_load(driver, By.ID, "tlpvt-passcode-input")

if user_id_input and password_input:
    user_id_input.send_keys(USER_ID)
    password_input.send_keys(PASSWORD)

submit_button = find_element_after_load(driver, By.ID, "login_button")
if submit_button:
    submit_button.click()

if not debug_mode:
    driver.quit()