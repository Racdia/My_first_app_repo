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

if option == "Scraping":
    st.header("Scraping de données")
    st.write("Scrapez des données à partir de plusieurs pages.")

    selected_category = st.selectbox("Choisir une catégorie :", ["Toutes les catégories"] + list(URLS.keys()))
    num_pages = st.number_input("Nombre de pages à scraper :", min_value=1, max_value=50, value=2)
    clean_data_option = st.checkbox("Nettoyer les données avant affichage", value=True)

    load_existing_data()

    if st.button("Lancer le scraping"):
        with st.spinner("Scraping en cours.."):
            if selected_category == "Toutes les catégories":
                for category, url in URLS.items():
                    scrap_data(url, category, max_pages=num_pages)
            else:
                scrap_data(URLS[selected_category], selected_category, max_pages=num_pages)
            st.rerun()

elif option == "Dashboard":
    st.header("📈 Dashboard des données scrapées")
    selected_dashboard_category = st.selectbox("Choisir une catégorie à analyser :", list(URLS.keys()))
    file_path = f"data/webscraper_data/{selected_dashboard_category.lower().replace(' ', '_')}.csv"
    try:
        df_dashboard = pd.read_csv(file_path)
        display_dashboard(df_dashboard, selected_dashboard_category)
    except FileNotFoundError:
        st.warning(f"⚠️ Aucune donnée trouvée pour {selected_dashboard_category}. Veuillez scraper d'abord.")

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

elif option == "Évaluer l'App":
    st.header("Évaluer l'application")
    st.write("Merci de remplir ce formulaire pour nous aider à améliorer l'application.")
    kobo_form_url = "https://ee.kobotoolbox.org/x/bCaC927U"
    iframe_code = f'<iframe src="{kobo_form_url}" width="100%" height="600px"></iframe>'
    st.markdown(iframe_code, unsafe_allow_html=True)

