import os
import time
import random
import requests
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OUTPUT_DIR = "photos"
IDS_FILE = "test_id.txt"
COOKIES_FILE = "google_cookies.pkl"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_stealth_options():
    options = Options()
    options.headless = False
    
    # Отключаем автоматизацию
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Базовые флаги
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    
    # Скрываем автоматизацию
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Реальный User-Agent
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Размер окна как у обычного пользователя
    options.add_argument("--window-size=1366,768")
    
    return options

def setup_stealth_driver(driver):
    # Убираем следы автоматизации
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Добавляем реальные свойства браузера
    driver.execute_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
    """)
    
    driver.execute_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['ru-RU', 'ru', 'en-US', 'en']
        });
    """)

def save_cookies(driver, filepath):
    """Сохранить cookies в файл"""
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(driver.get_cookies(), f)
        print("Cookies сохранены")
    except Exception as e:
        print(f"Ошибка при сохранении cookies: {e}")

def load_cookies(driver, filepath):
    """Загрузить cookies из файла"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print("Cookies загружены")
            return True
    except Exception as e:
        print(f"Ошибка при загрузке cookies: {e}")
    return False

def handle_google_consent(driver):
    """Обработка согласия Google"""
    try:
        # Ждем появления кнопки "Принять все" или "I agree"
        accept_buttons = [
            "//button[contains(text(), 'Принять все')]",
            "//button[contains(text(), 'Accept all')]", 
            "//button[contains(text(), 'I agree')]",
            "//div[contains(text(), 'Принять все')]",
            "//div[contains(text(), 'Accept all')]"
        ]
        
        for button_xpath in accept_buttons:
            try:
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, button_xpath))
                )
                button.click()
                print("Нажата кнопка согласия")
                time.sleep(2)
                return True
            except:
                continue
                
        # Если кнопки нет, возможно уже принято
        return True
        
    except Exception as e:
        print(f"Ошибка при обработке согласия: {e}")
        return False

def human_like_typing(element, text, min_delay=0.05, max_delay=0.15):
    """Имитация человеческого набора текста"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))

def random_mouse_movement(driver, actions):
    """Случайные движения мыши"""
    try:
        # Получаем размеры окна
        size = driver.get_window_size()
        width, height = size['width'], size['height']
        
        # Случайная точка для движения
        x = random.randint(100, width - 100)
        y = random.randint(100, height - 100)
        
        actions.move_by_offset(x, y).perform()
        time.sleep(random.uniform(0.5, 1.5))
        actions.move_by_offset(-x, -y).perform()  # Возвращаемся
    except:
        pass

def human_scroll(driver):
    """Человеческая прокрутка"""
    # Прокручиваем маленькими частями
    scroll_amount = random.randint(200, 400)
    for i in range(3):
        driver.execute_script(f"window.scrollBy(0, {scroll_amount // 3})")
        time.sleep(random.uniform(0.3, 0.8))

def handle_magnit_button(driver):
    """Обработка кнопки 'Изменить' на сайте Magnit"""
    try:
        # Ищем кнопку по разным селекторам
        button_selectors = [
            "button[data-test-id='v-button-base']:contains('Изменить')",
            "button .pl-button__title:contains('Изменить')",
            "//button[contains(@class, 'pl-button')]//span[contains(text(), 'Изменить')]",
            "//button[@data-test-id='v-button-base']//span[contains(text(), 'Изменить')]"
        ]
        
        for selector in button_selectors:
            try:
                if selector.startswith("//"):
                    # XPath селектор
                    button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    # CSS селектор (упрощенный, так как :contains не поддерживается)
                    continue
                
                button.click()
                print("Нажата кнопка 'Изменить'")
                time.sleep(1)
                return True
            except:
                continue
        
        # Альтернативный поиск по классу и тексту
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, "button.pl-button")
            for button in buttons:
                if "Изменить" in button.text:
                    button.click()
                    print("Нажата кнопка 'Изменить'")
                    time.sleep(1)
                    return True
        except:
            pass
            
        return False
        
    except Exception as e:
        print(f"Ошибка при поиске кнопки 'Изменить': {e}")
        return False

def download_image(url, product_id):
    try:
        # Добавляем реалистичные заголовки
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://cosmetic.magnit.ru/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        filename = os.path.join(OUTPUT_DIR, f"{product_id}.jpg")
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Скачано: {filename}")
    except Exception as e:
        print(f"Ошибка при скачивании изображения: {e}")

# Настройка драйвера
options = get_stealth_options()
driver = webdriver.Chrome(options=options)
setup_stealth_driver(driver)
actions = ActionChains(driver)

# Переходим на Google и загружаем cookies
print("Переход на Google...")
driver.get("https://www.google.com")
time.sleep(2)

# Пытаемся загрузить сохраненные cookies
cookies_loaded = load_cookies(driver, COOKIES_FILE)

if not cookies_loaded:
    print("Cookies не найдены, первый запуск...")
    # Обрабатываем согласие при первом запуске
    handle_google_consent(driver)
    time.sleep(3)
    # Сохраняем cookies после согласия
    save_cookies(driver, COOKIES_FILE)
else:
    print("Cookies загружены, обновляем страницу...")
    driver.refresh()
    time.sleep(2)

# Читаем ID товаров
with open(IDS_FILE, "r", encoding="utf-8") as f:
    product_ids = [line.strip() for line in f if line.strip()]

print(f"Найдено {len(product_ids)} товаров для обработки")

try:
    for i, pid in enumerate(product_ids):
        try:
            print(f"Обрабатываем товар {i+1}/{len(product_ids)}: {pid}")
            
            # Переходим на Google (cookies уже загружены)
            driver.get("https://www.google.com")
            time.sleep(random.uniform(2, 3))
            
            # Случайные движения мыши
            if random.choice([True, False]):
                random_mouse_movement(driver, actions)
            
            # Ищем поле поиска
            search_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "q"))
            )
            
            # Кликаем с задержкой
            actions.move_to_element(search_box).pause(random.uniform(0.3, 0.8)).click().perform()
            time.sleep(random.uniform(0.5, 1))
            
            # Печатаем поисковый запрос как человек
            search_query = f"site:cosmetic.magnit.ru {pid}"
            human_like_typing(search_box, search_query)
            
            # Случайная пауза перед поиском
            time.sleep(random.uniform(0.5, 1.5))
            
            # Нажимаем Enter
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(5, 10))
            
            # Ищем ссылку на товар
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='cosmetic.magnit.ru/product/']")
            found_link = None
            
            for link in links:
                href = link.get_attribute("href")
                if href and "cosmetic.magnit.ru/product/" in href:
                    found_link = href
                    break
            
            if not found_link:
                print(f"Товар {pid}: ссылка не найдена в результатах поиска")
                continue
            
            print(f"Товар {pid}: найдена ссылка {found_link}")
            
            # Переходим на страницу товара
            driver.get(found_link)
            time.sleep(random.uniform(2, 4))
            
            # Проверяем и нажимаем кнопку "Изменить" если есть
            handle_magnit_button(driver)
            
            # Имитируем чтение страницы
            human_scroll(driver)
            time.sleep(random.uniform(1, 2))
            
            # Случайные движения мыши на странице
            if random.choice([True, False]):
                random_mouse_movement(driver, actions)
            
            # Ищем изображение товара
            try:
                img = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img.product-details-gallery__slide-image"))
                )
                img_url = img.get_attribute("src")
                
                if img_url:
                    download_image(img_url, pid)
                else:
                    print(f"Товар {pid}: URL изображения не найден")
                    
            except Exception as e:
                print(f"Товар {pid}: изображение не найдено - {e}")
            
        except Exception as e:
            print(f"Ошибка с товаром {pid}: {e}")
        
        # Пауза между товарами
        if i < len(product_ids) - 1:  # Не ждем после последнего товара
            pause_time = random.uniform(5, 10)
            print(f"Пауза {pause_time:.1f} секунд перед следующим товаром...")
            time.sleep(pause_time)

finally:
    # Сохраняем cookies перед закрытием
    try:
        save_cookies(driver, COOKIES_FILE)
    except:
        pass
    driver.quit()
    print("Работа завершена")