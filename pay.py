from selenium import webdriver
import os

from dotenv import load_dotenv
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

debug_mode = True
load_dotenv()

script_path = Path(__file__).resolve().parent
driver_path = script_path.joinpath("chromedriver-win64", "chromedriver.exe")
brave_path = os.getenv("BRAVE_PATH")

chrome_options = Options()
chrome_options.binary_location = brave_path

service = Service(driver_path)

if debug_mode:
    print("In debug mode : ")
    chrome_options.add_experimental_option("detach", True)
else:
    chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://secure.bankofamerica.com/login/sign-in/signOnV2Screen.go")

driver.quit()