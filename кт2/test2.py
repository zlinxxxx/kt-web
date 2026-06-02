from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("http://quotes.toscrape.com")
time.sleep(2)


print("Тест 1: Главная страница загружается")
title = driver.title
assert "Quotes" in title
print("Тест 1 пройден — заголовок страницы:", title)


print("Тест 2: Цитаты отображаются на главной странице")
quotes = driver.find_elements(By.CLASS_NAME, "quote")
assert len(quotes) > 0
print("Тест 2 пройден — цитат на странице:", len(quotes))


print("Тест 3: Переход по тегу")
first_tag = driver.find_element(By.CSS_SELECTOR, ".quote .tag")
tag_text = first_tag.text
first_tag.click()
time.sleep(2)
quotes_on_tag_page = driver.find_elements(By.CLASS_NAME, "quote")
assert len(quotes_on_tag_page) > 0
print(f"Тест 3 пройден — цитат по тегу '{tag_text}':", len(quotes_on_tag_page))

driver.quit()
print("\nВсе тесты пройдены успешно!")
