from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

BASE = "https://the-internet.herokuapp.com"
results = []


def test(tc_id, name, func):
    try:
        status, actual = func()
        results.append({"id": tc_id, "name": name, "status": status, "actual": actual})
        mark = "PASS" if status == "Пройден" else "FAIL"
        print(f"[{mark}] {tc_id}: {name}")
        print(f"       Факт: {actual}\n")
    except Exception as e:
        results.append({"id": tc_id, "name": name, "status": "Ошибка", "actual": str(e)})
        print(f"[ERROR] {tc_id}: {name}")
        print(f"       Ошибка: {e}\n")


def _fresh_login_page():
    # Гарантированно выходим из сессии и открываем страницу логина
    try:
        driver.get(f"{BASE}/logout")
        time.sleep(0.5)
    except Exception:
        pass
    driver.delete_all_cookies()
    driver.get(f"{BASE}/login")
    wait.until(EC.presence_of_element_located((By.ID, "username")))


# ===== TC-002: Авторизация с невалидным логином =====
def tc002():
    _fresh_login_page()
    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "username").send_keys("wrong_user")
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    flash_el = wait.until(EC.presence_of_element_located((By.ID, "flash")))
    flash = flash_el.text.strip().split("\n")[0]
    if "your username is invalid" in flash.lower():
        return "Пройден", f"Сообщение об ошибке: «{flash}»"
    return "Провален", f"Неожиданное сообщение: {flash}"


test("TC-002", "Авторизация с невалидным логином", tc002)


# ===== TC-003: Авторизация с невалидным паролем =====
def tc003():
    _fresh_login_page()
    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "username").send_keys("tomsmith")
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys("wrong_password")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    flash_el = wait.until(EC.presence_of_element_located((By.ID, "flash")))
    flash = flash_el.text.strip().split("\n")[0]
    if "your password is invalid" in flash.lower():
        return "Пройден", f"Сообщение об ошибке: «{flash}»"
    return "Провален", f"Неожиданное сообщение: {flash}"


test("TC-003", "Авторизация с невалидным паролем", tc003)


# ===== TC-004: Авторизация с пустыми полями =====
def tc004():
    _fresh_login_page()
    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)
    try:
        flash = driver.find_element(By.ID, "flash").text.strip().split("\n")[0]
        if "invalid" in flash.lower():
            return "Пройден", f"Валидация сработала: «{flash}»"
        return "Провален", f"Неожиданное сообщение: {flash}"
    except Exception:
        return "Провален", "Сообщение об ошибке не найдено, валидация не сработала"


test("TC-004", "Авторизация с пустыми полями", tc004)


# ===== TC-001: Авторизация с валидными данными =====
def tc001():
    _fresh_login_page()
    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "username").send_keys("tomsmith")
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait.until(EC.url_contains("/secure"))
    url = driver.current_url
    flash = driver.find_element(By.ID, "flash").text.strip().split("\n")[0]
    if "secure" in url and "logged into a secure area" in flash.lower():
        return "Пройден", f"Перенаправлен на {url}. Сообщение: «{flash}»"
    return "Провален", f"URL: {url}, сообщение: {flash}"


test("TC-001", "Авторизация с валидными данными (tomsmith)", tc001)


# ===== TC-005: Чекбоксы — переключение состояний =====
def tc005():
    driver.get(f"{BASE}/checkboxes")
    cbs = driver.find_elements(By.CSS_SELECTOR, "#checkboxes input[type='checkbox']")
    before = [cb.is_selected() for cb in cbs]
    for cb in cbs:
        cb.click()
    time.sleep(0.5)
    cbs = driver.find_elements(By.CSS_SELECTOR, "#checkboxes input[type='checkbox']")
    after = [cb.is_selected() for cb in cbs]
    expected = [not b for b in before]
    if after == expected:
        return "Пройден", f"До клика: {before}, после клика: {after} — состояния инвертированы корректно"
    return "Провален", f"До: {before}, после: {after}, ожидалось: {expected}"


test("TC-005", "Переключение состояния чекбоксов", tc005)


# ===== TC-006: Dropdown — выбор опции =====
def tc006():
    driver.get(f"{BASE}/dropdown")
    select = Select(driver.find_element(By.ID, "dropdown"))
    select.select_by_visible_text("Option 2")
    time.sleep(0.5)
    selected = select.first_selected_option.text
    if selected == "Option 2":
        return "Пройден", f"Выбрана опция: «{selected}»"
    return "Провален", f"Выбрано: «{selected}», ожидалось: «Option 2»"


test("TC-006", "Выбор значения в выпадающем списке", tc006)


# ===== TC-007: Add/Remove Elements — добавление кнопок =====
def tc007():
    driver.get(f"{BASE}/add_remove_elements/")
    wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Add Element']")))
    for _ in range(3):
        # перепоиск каждый раз во избежание stale-reference
        btn = driver.find_element(By.XPATH, "//button[normalize-space()='Add Element']")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.3)
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "button.added-manually")) == 3)
    delete_btns = driver.find_elements(By.CSS_SELECTOR, "button.added-manually")
    if len(delete_btns) == 3:
        return "Пройден", f"Добавлено {len(delete_btns)} кнопок «Delete»"
    return "Провален", f"Кнопок «Delete»: {len(delete_btns)}, ожидалось: 3"


test("TC-007", "Динамическое добавление элементов на страницу", tc007)


# ===== TC-008: Add/Remove Elements — удаление элементов =====
def tc008():
    delete_btns = driver.find_elements(By.CSS_SELECTOR, "button.added-manually")
    initial = len(delete_btns)
    if initial == 0:
        return "Провален", "Нет элементов для удаления (TC-007 не отработал)"
    driver.execute_script("arguments[0].click();", delete_btns[0])
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "button.added-manually")) == initial - 1)
    remaining = driver.find_elements(By.CSS_SELECTOR, "button.added-manually")
    if len(remaining) == initial - 1:
        return "Пройден", f"Было {initial} кнопок, после удаления стало {len(remaining)}"
    return "Провален", f"Было {initial}, стало {len(remaining)}, ожидалось {initial - 1}"


test("TC-008", "Удаление динамически добавленного элемента", tc008)


# ===== TC-009: JavaScript Alerts — JS Confirm =====
def tc009():
    driver.get(f"{BASE}/javascript_alerts")
    driver.find_element(By.CSS_SELECTOR, "button[onclick='jsConfirm()']").click()
    time.sleep(0.5)
    alert = driver.switch_to.alert
    alert_text = alert.text
    alert.accept()
    time.sleep(0.5)
    result_text = driver.find_element(By.ID, "result").text
    if alert_text == "I am a JS Confirm" and "you clicked: ok" in result_text.lower():
        return "Пройден", f"Текст alert: «{alert_text}», результат: «{result_text}»"
    return "Провален", f"Alert: «{alert_text}», результат: «{result_text}»"


test("TC-009", "Принятие JavaScript Confirm-диалога", tc009)


# ===== TC-010: Dynamic Loading — ожидание появления элемента =====
def tc010():
    driver.get(f"{BASE}/dynamic_loading/2")
    driver.find_element(By.CSS_SELECTOR, "#start button").click()
    finish = wait.until(EC.visibility_of_element_located((By.ID, "finish")))
    text = finish.text.strip()
    if "hello world" in text.lower():
        return "Пройден", f"Элемент дождался отрисовки. Текст: «{text}»"
    return "Провален", f"Неожиданный текст: «{text}»"


test("TC-010", "Ожидание динамически загружаемого элемента (Dynamic Loading)", tc010)


# ===== TC-011: Hovers — наведение и отображение профиля =====
def tc011():
    driver.get(f"{BASE}/hovers")
    figure = driver.find_elements(By.CSS_SELECTOR, "div.figure")[0]
    ActionChains(driver).move_to_element(figure).perform()
    time.sleep(0.5)
    caption = figure.find_element(By.CSS_SELECTOR, "div.figcaption")
    displayed = caption.is_displayed()
    name = caption.find_element(By.TAG_NAME, "h5").text
    if displayed and "user1" in name.lower():
        return "Пройден", f"При наведении отобразилось имя: «{name}»"
    return "Провален", f"displayed={displayed}, name={name}"


test("TC-011", "Появление информации о пользователе при наведении (Hovers)", tc011)


# ===== TC-012: Проверка корректности отображения изображений =====
def tc012():
    driver.get(f"{BASE}/broken_images")
    images = driver.find_elements(By.CSS_SELECTOR, "div.example img")
    total = len(images)
    broken = []
    for i, img in enumerate(images, 1):
        natural_w = driver.execute_script("return arguments[0].naturalWidth;", img)
        src = img.get_attribute("src").split("/")[-1]
        if natural_w == 0:
            broken.append(src)
    if not broken:
        return "Пройден", f"Все {total} изображений загрузились корректно"
    return "Провален", (
        f"Из {total} изображений {len(broken)} не загрузились "
        f"(naturalWidth=0): {', '.join(broken)}. На странице присутствуют битые изображения."
    )


test("TC-012", "Проверка корректности загрузки изображений на странице", tc012)


# ===== ИТОГ =====
results.sort(key=lambda r: r["id"])
print("=" * 60)
print("ИТОГИ ТЕСТИРОВАНИЯ")
print("=" * 60)
passed = sum(1 for r in results if r["status"] == "Пройден")
failed = sum(1 for r in results if r["status"] == "Провален")
errors = sum(1 for r in results if r["status"] == "Ошибка")
print(f"Всего: {len(results)} | Пройдено: {passed} | Провалено: {failed} | Ошибок: {errors}")
print(f"Успешность: {round(passed / len(results) * 100)}%")
print("=" * 60)

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

driver.quit()
