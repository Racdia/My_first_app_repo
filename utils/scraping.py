import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS = {
    "Chiens": "https://sn.coinafrique.com/categorie/chiens?page={}",
    "Moutons": "https://sn.coinafrique.com/categorie/moutons?page={}",
    "Poules": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons?page={}",
    "Autres": "https://sn.coinafrique.com/categorie/autres-animaux?page={}"
}

def scrap_data(base_url, category, max_pages=1):
    all_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/132.0.0.0 Safari/537.36"
    }

    for page_num in range(1, max_pages + 1):
        url = base_url.format(page_num)
        print(f"🔍 Scraping de la page {page_num} : {url}")

        response = requests.get(url, headers=headers, verify=False)
        if response.status_code != 200:
            print(f"⚠️ Erreur sur la page {page_num} : HTTP {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        containers = soup.select("div.col.s6.m4.l3")
        print(f"🔎 Trouvé {len(containers)} annonces sur la page {page_num}")

        for container in containers:
            try:
                details_elem = container.select_one(".ad__card-description")
                details = details_elem.get_text(strip=True) if details_elem else "N/A"

                price_elem = container.select_one(".ad__card-price")
                location_elem = container.select_one(".ad__card-location")

                price_text = price_elem.get_text(strip=True).replace("FCFA", "").replace(",", "").strip() if price_elem else "N/A"
                location_text = location_elem.get_text(strip=True) if location_elem else "N/A"

                image_element = container.select_one("img")
                image_url = image_element["src"].strip() if image_element and image_element.has_attr("src") else "N/A"

                all_data.append({
                    "Détails": details,
                    "Prix": price_text,
                    "Localisation": location_text,
                    "Image URL": image_url
                })
            except Exception as e:
                print(f"⚠️ Erreur lors de l'extraction d'une annonce : {e}")

        time.sleep(3)

    file_path = f"data/selenium_data/{category.lower().replace(' ', '_')}.csv"
    if os.path.exists(file_path):
        try:
            old_df = pd.read_csv(file_path)
            if old_df.empty:
                print(f"⚠️ Le fichier {file_path} est vide, il sera ignoré.")
                old_df = pd.DataFrame()
            else:
                print(f"📂 Chargement des anciennes données depuis : {file_path}")
        except pd.errors.EmptyDataError:
            print(f"⚠️ Erreur : Le fichier {file_path} est vide ou corrompu. Il sera ignoré.")
            old_df = pd.DataFrame()
    else:
        old_df = pd.DataFrame()

    if all_data:
        new_df = pd.DataFrame(all_data)
        combined_df = pd.concat([old_df, new_df], ignore_index=True).drop_duplicates()
        combined_df.to_csv(file_path, index=False)
        print(f"✅ Données sauvegardées pour {category} dans : {file_path}")
    else:
        print(f"⚠️ Aucun nouveau résultat. Conservation des anciennes données.")

for category, url in URLS.items():
    scrap_data(url, category)
