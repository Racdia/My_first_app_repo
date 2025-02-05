import time
import requests
from bs4 import BeautifulSoup

# URLs des catégories
URLS = {
    "Véhicules": "https://dakarvente.com/index.php?page=annonces_rubrique&url_categorie_2=vehicules&id=2&sort=&nb={}",
    "Motos": "https://dakarvente.com/index.php?page=annonces_categorie&id=3&sort=&nb={}",
    "Voitures en location": "https://dakarvente.com/index.php?page=annonces_categorie&id=8&sort=&nb={}",
    "Téléphones": "https://dakarvente.com/index.php?page=annonces_categorie&id=32&sort=&nb={}"
}


def scrap_data(base_url, max_pages=10):
    all_data = []
    # Utiliser un User-Agent pour simuler un navigateur
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/114.0.0.0 Safari/537.36"
    }

    for page_num in range(1, max_pages + 1):
        url = base_url.format(page_num)
        print(f"Scraping de la page {page_num} : {url}")
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"⚠️ Erreur sur la page {page_num} : HTTP {response.status_code}")
            continue

        # Parser le contenu HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Sélectionner les conteneurs d'annonce
        containers = soup.select(".item-inner.mv-effect-translate-1.mv-box-shadow-gray-1")
        print(f"Trouvé {len(containers)} conteneurs sur la page {page_num}")

        for container in containers:
            try:
                # Extraire les détails de l'annonce
                details_elem = container.find(class_="content-desc")
                details = details_elem.get_text(strip=True) if details_elem else "N/A"

                # Extraire les informations de prix et localisation
                prices_elements = container.find_all(class_="content-price")
                if prices_elements:
                    price_text = prices_elements[0].get_text(strip=True).replace("FCFA", "").replace(",", "").strip()
                    location_text = prices_elements[1].get_text(strip=True) if len(prices_elements) > 1 else "N/A"
                else:
                    price_text = "N/A"
                    location_text = "N/A"

                # Extraire l'URL de l'image
                image_element = container.select_one("h2 a img")
                image_url = image_element["src"].strip() if image_element and image_element.has_attr("src") else "N/A"

                all_data.append({
                    "détails": details,
                    "prix": price_text,
                    "localisation": location_text,
                    "image URL": image_url
                })
            except Exception as e:
                print("⚠️ Erreur lors de l'extraction d'une annonce :", e)

        # Pause pour éviter de surcharger le serveur
        time.sleep(1)

    return all_data



