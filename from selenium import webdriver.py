from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
chrome_binary = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
driver_path = r"C:\Users\victor\Desktop\chromedriver-win64\chromedriver.exe"
options = Options()
options.binary_location = chrome_binary
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.google.com")
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("Selenium для новичков")
search_box.send_keys(Keys.RETURN)
time.sleep(30)
driver.quit()
