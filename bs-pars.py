import os
import time
import random
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

BASE_URL = "https://cosmetic.magnit.ru/catalog/?page={}"
OUTPUT_DIR = "photos"
CODES_FILE = "product_ids.txt"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(CODES_FILE, "r", encoding="utf-8") as f:
    product_ids = [line.strip() for line in f if line.strip()]

options = Options()
options.headless = True
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

stats = {"downloaded": 0, "not_found": 0, "download_error": 0}

def download_image(url, folder=OUTPUT_DIR, product_id=None):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        ext = ".jpg"
        filename = f"{product_id}{ext}" if product_id else f"image{ext}"
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Фото сохранено: {filepath}")
        stats["downloaded"] += 1
    except Exception as e:
        print(f"Ошибка скачивания {url}: {e}")
        stats["download_error"] += 1

def download_product_photo(product_id):
    page = 1
    found = False
    while page <= 28:
        url = BASE_URL.format(page)
        print(f"Парсинг страницы {page}...")

        driver.get(url)
        time.sleep(random.uniform(3, 5))

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        items = soup.find_all("div", {"data-test-id": "v-stack-item"})
        if not items:
            print("Больше товаров нет.")
            break

        for item in items:
            a_tag = item.find("a", href=True)
            if not a_tag:
                continue

            match = re.search(r'/product/(\d+)-', a_tag['href'])
            if not match:
                continue

            current_product_id = match.group(1)

            if current_product_id != product_id:
                continue

            img_tag = item.select_one("div.unit-catalog-product-preview-gallery img")
            if img_tag:
                img_url = img_tag.get("src", "")
                if img_url.startswith("http"):
                    print(f"Product {product_id}: photo url = {img_url}")
                    download_image(img_url, product_id=product_id)
                else:
                    print(f"Product {product_id}: найден src, но не ссылка: {img_url}")
                    stats["not_found"] += 1
            else:
                print(f"Product {product_id}: фото не найдено")
                stats["not_found"] += 1
            found = True
            break

        if found:
            break

        page += 1
        time.sleep(random.uniform(1, 3))

for pid in product_ids:
    download_product_photo(pid)

driver.quit()

print("\nСтатистика:")
print(f"Фото успешно скачано: {stats['downloaded']}")
print(f"Фото не найдено: {stats['not_found']}")
print(f"Ошибок при скачивании: {stats['download_error']}")
