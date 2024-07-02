from selenium import webdriver
import os

from dotenv import load_dotenv
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

debug_mode = True
load_dotenv()

BRAVE_PATH = os.getenv("BRAVE_PATH")
USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")

script_path = Path(__file__).resolve().parent
driver_path = script_path.joinpath("chromedriver-win64", "chromedriver.exe")

chrome_options = Options()
chrome_options.binary_location = BRAVE_PATH

service = Service(driver_path)

if debug_mode:
    print("In debug mode : ")
    chrome_options.add_experimental_option("detach", True)
else:
    chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://secure.bankofamerica.com/login/sign-in/signOnV2Screen.go")

user_id_input = driver.find_element(By.ID, "enterID-input")
password_input = driver.find_element(By.ID, "tlpvt-passcode-input")

if user_id_input and password_input:
    user_id_input.send_keys(USER_ID)
    password_input.send_keys(PASSWORD)

if not debug_mode:
    driver.quit()