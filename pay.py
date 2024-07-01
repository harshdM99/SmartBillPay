from selenium import webdriver
from pathlib import Path
from selenium.webdriver.chrome.service import Service

script_path = Path(__file__).resolve().parent
driver_path = script_path.joinpath("chromedriver-win64", "chromedriver.exe")

# print(script_path)
print(driver_path)
# print(type(script_path))

service = Service(driver_path)

driver = webdriver.Chrome(service=service)
driver.get("https://www.google.com")

driver.quit()