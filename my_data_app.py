import streamlit as st
import pandas as pd
import os
import base64
import time
import requests
from bs4 import BeautifulSoup
import urllib3

from utils.cleaning import clean_data
from utils.dashboard import display_dashboard
from utils.scraping import scrap_data

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="My Scraping App", page_icon="🚀", layout="wide")

st.sidebar.title("Menu")

URLS = {
    "chiens": "https://sn.coinafrique.com/categorie/chiens?page={}",
    "moutons": "https://sn.coinafrique.com/categorie/moutons?page={}",
    "poules": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons?page={}",
    "autres": "https://sn.coinafrique.com/categorie/autres-animaux?page={}"
}
option = st.sidebar.radio(
    "Choisir une option :",
    ("Scraping", "Dashboard", "WebScraper Data", "Évaluer l'App")
)

# 📌 Scraping
# def scrap_data(base_url, category, max_pages=10):
#     all_data = []
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                       "Chrome/132.0.0.0 Safari/537.36"
#     }
#
#     for page_num in range(1, max_pages + 1):
#         url = base_url.format(page_num)
#         print(f"🔍 Scraping de la page {page_num} : {url}")
#
#         # Vérifier si l'URL est valide avant de scraper
#         response = requests.head(url, headers=headers, verify=False)
#         if response.status_code == 404:
#             print(f"⚠️ La page {page_num} n'existe pas (HTTP 404). Arrêt du scraping.")
#             break  # Arrêter le scraping si la page n'existe pas
#
#         response = requests.get(url, headers=headers, verify=False)
#         if response.status_code != 200:
#             print(f"⚠️ Erreur sur la page {page_num} : HTTP {response.status_code}")
#             continue
#
#         soup = BeautifulSoup(response.text, "html.parser")
#
#         containers = soup.select(".item-inner.mv-effect-translate-1.mv-box-shadow-gray-1")
#         print(f"🔎 Trouvé {len(containers)} annonces sur la page {page_num}")
#
#         for container in containers:
#             try:
#                 details_elem = container.find(class_="content-desc")
#                 details = details_elem.get_text(strip=True) if details_elem else "N/A"
#
#                 prices_elements = container.find_all(class_="content-price")
#                 if prices_elements:
#                     price_text = prices_elements[0].get_text(strip=True).replace("FCFA", "").replace(",", "").strip()
#                     location_text = prices_elements[1].get_text(strip=True) if len(prices_elements) > 1 else "N/A"
#                 else:
#                     price_text = "N/A"
#                     location_text = "N/A"
#
#                 image_element = container.select_one("h2 a img")
#                 image_url = image_element["src"].strip() if image_element and image_element.has_attr("src") else "N/A"
#
#                 all_data.append({
#                     "détails": details,
#                     "prix": price_text,
#                     "localisation": location_text,
#                     "image URL": image_url
#                 })
#             except Exception as e:
#                 print(f"⚠️ Erreur lors de l'extraction d'une annonce : {e}")
#
#         # Délai pour éviter d’être bloqué par le site
#         time.sleep(3)
#
#     # 📌 Vérification des données existantes
#     file_path = f"data/{category.lower().replace(' ', '_')}.csv"
#     if os.path.exists(file_path):
#         print(f"📂 Chargement des anciennes données depuis : {file_path}")
#         old_df = pd.read_csv(file_path)
#     else:
#         old_df = pd.DataFrame()
#
#     # 📌 Fusion des nouvelles et anciennes données uniquement si du nouveau contenu a été scrapé
#     if all_data:
#         new_df = pd.DataFrame(all_data)
#         combined_df = pd.concat([old_df, new_df], ignore_index=True).drop_duplicates()
#         combined_df.to_csv(file_path, index=False)
#         print(f"✅ Données sauvegardées pour {category} dans : {file_path}")
#     else:
#         print(f"⚠️ Aucun nouveau résultat. Conservation des anciennes données.")

# 📌 Fonction pour charger les anciennes données
def load_existing_data():
    if selected_category == "Toutes les catégories":
        for category in URLS.keys():
            file_path = f"data/selenium_data/{category.lower().replace(' ', '_')}.csv"
            try:
                df = pd.read_csv(file_path)
                if clean_data_option:
                    df = clean_data(df)
                st.markdown(f"### 📊 Données existantes pour **{category}**")
                st.dataframe(df)
            except FileNotFoundError:
                st.warning(f"⚠️ Aucune donnée existante pour {category}.")
    else:
        file_path = f"data/selenium_data/{selected_category.lower().replace(' ', '_')}.csv"
        try:
            df = pd.read_csv(file_path)
            if clean_data_option:
                df = clean_data(df)
            st.markdown(f"### 📊 Données existantes pour **{selected_category}**")
            st.dataframe(df)
        except FileNotFoundError:
            st.warning(f"⚠️ Aucune donnée existante pour {selected_category}.")

# 📌 Gestion du Scraping
if option == "Scraping":
    st.header("Scraping de données")
    st.write("Scrapez des données à partir de plusieurs pages.")

    selected_category = st.selectbox("Choisir une catégorie :", ["Toutes les catégories"] + list(URLS.keys()))
    num_pages = st.number_input("Nombre de pages à scraper :", min_value=1, max_value=50, value=2)
    clean_data_option = st.checkbox("Nettoyer les données avant affichage", value=True)

    load_existing_data()

    if st.button("Lancer le scraping"):
        with st.spinner("Scraping en cours..."):
            if selected_category == "Toutes les catégories":
                for category, url in URLS.items():
                    scrap_data(url, category, max_pages=num_pages)
            else:
                scrap_data(URLS[selected_category], selected_category, max_pages=num_pages)
            st.rerun()

# 📌 Gestion du Dashboard
elif option == "Dashboard":
    st.header("📈 Dashboard des données scrapées")
    selected_dashboard_category = st.selectbox("Choisir une catégorie à analyser :", list(URLS.keys()))
    file_path = f"data/webscraper_data/{selected_dashboard_category.lower().replace(' ', '_')}.csv"
    try:
        df_dashboard = pd.read_csv(file_path)
        display_dashboard(df_dashboard, selected_dashboard_category)
    except FileNotFoundError:
        st.warning(f"⚠️ Aucune donnée trouvée pour {selected_dashboard_category}. Veuillez scraper d'abord.")

# 📌 Option pour télécharger les données
elif option == "WebScraper Data":
    st.header("🌐 Données WebScraper")
    data_folder = "data/webscraper_data"
    if not os.path.exists(data_folder):
        st.warning("⚠️ Aucune donnée trouvée. Scrapez d'abord !")
    else:
        for file in os.listdir(data_folder):
            file_path = os.path.join(data_folder, file)
            with open(file_path, "rb") as f:
                st.download_button(f"⬇️ Télécharger {file}", data=f, file_name=file)

# 📌 Évaluation de l'application
elif option == "Évaluer l'App":
    st.header("Évaluer l'application")
    st.write("Merci de remplir ce formulaire pour nous aider à améliorer l'application.")
    kobo_form_url = "https://ee.kobotoolbox.org/x/bCaC927U"  # Remplace par ton propre lien
    iframe_code = f'<iframe src="{kobo_form_url}" width="100%" height="600px"></iframe>'
    st.markdown(iframe_code, unsafe_allow_html=True)

