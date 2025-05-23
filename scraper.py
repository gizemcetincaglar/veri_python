from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import sys

# ✅ Komut satırından URL alınır
if len(sys.argv) < 2:
    print("❌ Lütfen ürün URL'sini parametre olarak girin.")
    print("Örnek: python scraper.py https://www.trendyol.com/.../p-123")
    exit()

url = sys.argv[1]

# Tarayıcı ayarları
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Ürün sayfasını aç
driver.get(url)
time.sleep(3)

# Sayfanın sonuna kadar scroll yap (satıcılar yüklensin)
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# "Daha Fazla Satıcı Göster" butonuna tıkla
try:
    button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.omc-mr-btn.gnr-cnt-br"))
    )
    driver.execute_script("arguments[0].click();", button)
    print("✅ 'Daha Fazla Satıcı Göster' butonuna tıklandı.")
    time.sleep(2)
except:
    print("ℹ️ 'Daha Fazla Satıcı Göster' butonu bulunamadı veya zaten tıklanmış.")

# Sayfanın HTML'ini al
soup = BeautifulSoup(driver.page_source, "lxml")
driver.quit()

# Satıcı linklerini çek (class: pr-om-lnk-btn)
merchant_links = soup.select("a.pr-om-lnk-btn")

data = []
for link in merchant_links:
    href = link.get("href")
    if href and "merchantId=" in href:
        full_url = f"https://www.trendyol.com{href}"
        data.append({"seller_page": full_url})

# CSV'ye yaz
df = pd.DataFrame(data)
os.makedirs("output", exist_ok=True)
df.to_csv("output/data.csv", index=False)

print(f"📦 Toplam {len(df)} satıcı linki başarıyla çekildi.")
