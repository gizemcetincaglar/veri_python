from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import json, time, os

def extract_rating(html: str) -> str:
    """Sayfa HTML’inden sadece JSON-LD içindeki rating’i döndürür."""
    soup = BeautifulSoup(html, "lxml")
    for s in soup.select("script[type='application/ld+json']"):
        try:
            data = json.loads(s.string)
            if isinstance(data, dict) and "aggregateRating" in data:
                return str(data["aggregateRating"].get("ratingValue"))
        except Exception:
            continue
    return "Bilgi Yok"


# Headless tarayıcı ayarı
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Satıcı linklerini oku
df_links = pd.read_csv("output/data.csv")

data = []

for i, row in df_links.iterrows():
    url = row["seller_page"]
    driver.get(url)
    time.sleep(2)

    # Ürün başlığı
    try:
        product_name = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.pr-new-br"))
        ).text
    except:
        product_name = "Bilgi Yok"

    # Satıcı adı
    try:
        seller = driver.find_element(By.CSS_SELECTOR, ".merchant-name").text
    except:
        seller = "Bilgi Yok"

    # Fiyat
    try:
        price_raw = driver.find_element(By.CSS_SELECTOR, ".prc-dsc").text
        price = float(
            price_raw.replace(" TL", "").replace(".", "").replace(",", ".").strip()
        )
    except:
        price = 0.0

    # Rating – yeni yöntem
    rating = extract_rating(driver.page_source)

    # Kargo
    try:
        shipping = driver.find_element(
            By.XPATH, "//*[contains(text(),'Tahmini Kargoya Teslim')]"
        ).text
    except:
        shipping = "Bilgi Yok"

    data.append(
        {
            "product_name": product_name,
            "seller": seller,
            "price": price,
            "rating": rating,
            "shipping": shipping,
            "link": url,
        }
    )

    print(f"{i + 1}. satıcıdan veri alındı")

driver.quit()

# CSV’ye kaydet
df = pd.DataFrame(data)
os.makedirs("output", exist_ok=True)
df.to_csv("output/detailed_data.csv", index=False, encoding="utf-8-sig")
print("Tüm veriler 'output/detailed_data.csv' dosyasına kaydedildi.")
