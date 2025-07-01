import requests
import re
import time
import random

BASE_URL = "https://cosmetic.magnit.ru/catalog/?page={}"
TOTAL_PAGES = 28
OUTPUT_FILE = "product_ids.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
}

COOKIES = {
    "_yasc": "9aO6Ifn54TVYukpycwCZk7/DYSY0Lr8/xtENhskSYWq1I7x76k9go5ll6Z0j3i1C1ZLX",
    "_ym_d": "1751308780",
    "_ym_isad": "1",
    "_ym_uid": "1746275397813517053",
    "_ym_visorc": "b",
    "bh": "EkAiTm90KUE7QnJhbmQiO3Y9IjgiLCAiQ2hyb21pdW0iO3Y9IjEzOCIsICJHb29nbGUgQ2hyb21lIjt2PSIxMzgiGgN4ODYiDTEzOC4wLjcyMDQuNDkqAj8wOgkiV2luZG93cyJCBjE5LjAuMEoCNjRSWCJOb3QpQTtCcmFuZCI7dj0iOC4wLjAuMCIsIkNocm9taXVtIjt2PSIxMzguMC43MjA0LjQ5IiwiR29vZ2xlIENocm9tZSI7dj0iMTM4LjAuNzIwNC40OSJg+7OLwwZqHtzK4f8IktihsQOfz+HqA/v68OcN6//99g+K1M2HCA==",
    "das_d_tag2": "957a1ec8-4e79-4103-a5c6-9b97928161ae",
    "i": "XY+nBzsocPa1i+SKJFQvkZXvjQ3dHAJEhRH4u8CM9i9lU3yg/yJuNqbHwPBZTw4xHGpolA1K7EI5d5Em34vQZaQJhcU=",
    "mg_uac": "1",
    "mg_udi": "C928605F-4A1A-1346-DF74-FB9BED63C1B0",
    "nmg_cty": "%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3",
    "nmg_sp": "Y",
    "oxxfgh": "819ebdcb-04e1-4706-92d5-54125480b05e%230%237884000000%235000%231800000%2312840",
    "receive-cookie-deprecation": "1",
    "shopCode": "975690",
    "uwyiert": "cfc97bf5-0f0f-2fa8-3c86-c4df757780b7",
    "uwyii": "6e8dc585-c372-ac74-eceb-734759117088",
}

product_ids = set()

for page in range(1, TOTAL_PAGES + 1):
    url = BASE_URL.format(page)
    print(f"Загружаем страницу {page}...")
    response = requests.get(url, headers=HEADERS, cookies=COOKIES)
    if response.status_code == 200:
        found_ids = re.findall(r'/product/(\d+)-', response.text)
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
