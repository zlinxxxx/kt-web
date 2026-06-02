from selenium import webdriver
from selenium.webdriver.common.by import By
import time




class LoginPage:
    URL = "https://the-internet.herokuapp.com/login"

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    def enter_username(self, username):
        self.driver.find_element(By.ID, "username").send_keys(username)

    def enter_password(self, password):
        self.driver.find_element(By.ID, "password").send_keys(password)

    def click_login(self):
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    def is_logged_in(self):
        try:
            msg = self.driver.find_element(By.ID, "flash")
            return "You logged into a secure area" in msg.text
        except:
            return False




USERNAME = "tomsmith"
PASSWORD = "SuperSecretPassword!"

driver = webdriver.Chrome()
login_page = LoginPage(driver)

print("Тест: Авторизация на сайте the-internet.herokuapp.com")

# 1. Открыть страницу логина
login_page.open()
time.sleep(2)
print("Страница логина открыта")

# 2. Ввести логин и пароль
login_page.enter_username(USERNAME)
login_page.enter_password(PASSWORD)
time.sleep(1)
print("Логин и пароль введены")

# 3. Нажать кнопку входа
login_page.click_login()
time.sleep(2)
print("Кнопка входа нажата")

# 4. Проверить, что пользователь успешно авторизован
assert login_page.is_logged_in(), "Ошибка: пользователь не авторизован!"
print("Тест пройден — пользователь успешно авторизован!")

driver.quit()
