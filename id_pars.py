import requests
import re
import time
import random

BASE_URL = "https://cosmetic.magnit.ru/catalog/?page={}"
TOTAL_PAGES = 28
OUTPUT_FILE = "product_ids.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

product_ids = set()

for page in range(1, TOTAL_PAGES + 1):
    url = BASE_URL.format(page)
    print(f"Загружаем страницу {page}...")
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        html = response.text
        found_ids = re.findall(r'/product/(\d+)-', html)
        print(f"Найдено ID товаров на странице: {len(found_ids)}")
        product_ids.update(found_ids)
    else:
        print(f"Ошибка при загрузке страницы {page}: {response.status_code}")
    time.sleep(random.uniform(2, 4))

print(f"\nВсего уникальных ID товаров найдено: {len(product_ids)}")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for pid in sorted(product_ids):
        f.write(pid + "\n")

print(f"Сохранены в файл {OUTPUT_FILE}")
