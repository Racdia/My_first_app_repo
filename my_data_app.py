import streamlit as st
import pandas as pd
import os
import base64
import matplotlib as plt
import seaborn as sns

from utils.cleaning import clean_data
from utils.dashboard import display_dashboard
from utils.scraping import scrap_data

# Configuration de l'application
st.set_page_config(page_title="My Scraping App", page_icon="🚀", layout="wide")

# Sidebar (Menu latéral)
st.sidebar.title("Menu")

# Définition du chemin de l'image de fond
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as file:
        return base64.b64encode(file.read()).decode()

def set_background(image_path):
    if os.path.exists(image_path):
        base64_img = get_base64_of_bin_file(image_path)
        st.markdown(
            f"""
            <style>
                .stApp {{
                    background: url(data:image/png;base64,{base64_img}) no-repeat center center fixed;
                    background-size: cover;
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <style>
                .stApp {{
                    background-color: #f0f0f0;
                }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Charger l'image de fond automatiquement depuis le projet
background_image_path = "assets/data.PNG"  # Changez le chemin selon votre projet
#set_background(background_image_path)

# Titre de l'application
st.title("🚀 My Scraping App")

URLS = {
    "véhicules": "https://dakarvente.com/index.php?page=annonces_rubrique&url_categorie_2=vehicules&id=2&sort=&nb={}",
    "motos": "https://dakarvente.com/index.php?page=annonces_categorie&id=3&sort=&nb={}",
    "voitures en location": "https://dakarvente.com/index.php?page=annonces_categorie&id=8&sort=&nb={}",
    "téléphones": "https://dakarvente.com/index.php?page=annonces_categorie&id=32&sort=&nb={}"
}

option = st.sidebar.radio(
    "Choisir une option :",
    ("Scraping", "Dashboard", "WebScraper Data", "Évaluer l'App")
)

# Option 1 : Scraping
if option == "Scraping":
    st.header("Scraping de données")
    st.write("Scrapez des données à partir de plusieurs pages.")

    selected_category = st.selectbox("Choisir une catégorie :", ["Toutes les catégories"] + list(URLS.keys()))
    num_pages = st.number_input("Nombre de pages à scraper :", min_value=1, max_value=50, value=2)
    clean_data_option = st.checkbox("Nettoyer les données avant affichage", value=True)

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
            file_path = f"data/{selected_category.lower().replace(' ', '_')}.csv"
            try:
                df = pd.read_csv(file_path)
                if clean_data_option:
                    df = clean_data(df)
                st.markdown(f"### 📊 Données existantes pour **{selected_category}**")
                st.dataframe(df)
            except FileNotFoundError:
                st.warning(f"⚠️ Aucune donnée existante pour {selected_category}.")

    load_existing_data()

    if st.button("Lancer le scraping"):
        with st.spinner("Scraping en cours..."):
            if selected_category == "Toutes les catégories":
                all_data = {}
                for category, url in URLS.items():
                    st.markdown(f"### 🔄 Scraping des **{category}**...")
                    data = scrap_data(url, max_pages=num_pages)
                    df = pd.DataFrame(data)
                    if clean_data_option:
                        df = clean_data(df)
                    all_data[category] = df
                    st.markdown(f"### 📊 Données des {category}")
                    st.dataframe(df)
                    st.write("---")
                for category, df in all_data.items():
                    file_path = f"data/selenium_data/{category.lower().replace(' ', '_')}.csv"
                    df.to_csv(file_path, index=False)
                    st.success(f"Données sauvegardées pour {category} dans : `{file_path}`")
            else:
                data = scrap_data(URLS[selected_category], max_pages=num_pages)
                df = pd.DataFrame(data)
                if clean_data_option:
                    df = clean_data(df)
                st.markdown(f"### 📊 Données des {selected_category}")
                st.dataframe(df)
                file_path = f"data/{selected_category.lower().replace(' ', '_')}.csv"
                df.to_csv(file_path, index=False)
                st.success(f"Données sauvegardées dans : `{file_path}`")
            st.rerun()

# Option 2 : Dashboard
elif option == "Dashboard":
    st.header("📈 Dashboard des données scrapées")

    # Sélection de la catégorie
    selected_dashboard_category = st.selectbox("Choisir une catégorie à analyser :", list(URLS.keys()))

    file_path = f"data/webscraper_data/{selected_dashboard_category.lower().replace(' ', '_')}.csv"
    try:
        df_dashboard = pd.read_csv(file_path)

        clean_data(df_dashboard)
        display_dashboard(df_dashboard, selected_dashboard_category)

    except FileNotFoundError:
        st.warning(f"⚠️ Aucune donnée trouvée pour {selected_dashboard_category}. Veuillez scraper d'abord.")

# Option 3 : WebScraper Data
elif option == "WebScraper Data":
    st.header("🌐 Données WebScraper")
    st.write("Téléchargez les fichiers de données scrapées disponibles dans `data/`.")

    # Vérifier l'existence du dossier "data"
    data_folder = "data/webscraper_data"
    if not os.path.exists(data_folder):
        st.warning("⚠️ Le dossier 'data/' est introuvable. Veuillez d'abord scraper des données.")
    else:
        # Liste des fichiers disponibles dans le dossier 'data/'
        files = [f for f in os.listdir(data_folder) if f.endswith(".csv") or f.endswith(".json")]

        if files:
            for file in files:
                file_path = os.path.join(data_folder, file)

                # Lire le fichier pour le téléchargement
                with open(file_path, "rb") as f:
                    file_bytes = f.read()

                # Affichage avec icône de téléchargement
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📄 {file}")
                with col2:
                    st.download_button(
                        label="⬇️",
                        data=file_bytes,
                        file_name=file,
                        mime="text/csv" if file.endswith(".csv") else "application/json"
                    )
        else:
            st.warning("⚠️ Aucun fichier disponible dans `data/`. Veuillez d'abord scraper des données.")

# Option 4 : Évaluer l'App
elif option == "Évaluer l'App":
    st.header("Évaluer l'application")
    st.write("Merci de remplir ce formulaire pour nous aider à améliorer l'application.")

    kobo_form_url = "https://ee.kobotoolbox.org/x/bCaC927U"  # Remplace par ton propre lien
    iframe_code = f'<iframe src="{kobo_form_url}" width="100%" height="600px"></iframe>'
    st.markdown(iframe_code, unsafe_allow_html=True)
