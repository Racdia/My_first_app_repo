import streamlit as st
import pandas as pd
import time
import re
import matplotlib.pyplot as plt
import seaborn as sns
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuration de Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# URLs des catégories
URLS = {
    "Véhicules": "https://dakarvente.com/index.php?page=annonces_rubrique&url_categorie_2=vehicules&id=2&sort=&nb={}",
    "Motos": "https://dakarvente.com/index.php?page=annonces_categorie&id=3&sort=&nb={}",
    "Voitures en location": "https://dakarvente.com/index.php?page=annonces_categorie&id=8&sort=&nb={}",
    "Téléphones": "https://dakarvente.com/index.php?page=annonces_categorie&id=32&sort=&nb={}"
}

# Fonction de scraping
def scrap_data(base_url, max_pages=10):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    all_data = []

    for page in range(1, max_pages + 1):
        url = base_url.format(page)
        driver.get(url)
        time.sleep(5)

        try:
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".item-inner.mv-effect-translate-1.mv-box-shadow-gray-1")))

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            containers = driver.find_elements(By.CSS_SELECTOR, ".item-inner.mv-effect-translate-1.mv-box-shadow-gray-1")

            for container in containers:
                try:
                    details = container.find_element(By.CLASS_NAME, 'content-desc').text.strip()
                    prices = container.find_elements(By.CLASS_NAME, 'content-price')
                    price = prices[0].text.replace('FCFA', '').replace(',', '').strip() if prices else "N/A"
                    location = prices[1].text.strip() if len(prices) > 1 else "N/A"
                    image_element = container.find_element(By.CSS_SELECTOR, "h2 a img")
                    image_url = image_element.get_attribute("src").strip()

                    all_data.append({'Détails': details, 'Prix': price, 'Localisation': location, 'Image URL': image_url})

                except Exception as e:
                    print("⚠️ Erreur lors de l'extraction d'une annonce :", e)

        except Exception as e:
            print(f"⚠️ Erreur sur la page {page}: {e}")

    driver.quit()
    return all_data

# Fonction de nettoyage des données
def clean_data(df):
    df = df.copy()
    if "Prix" in df.columns:
        # Convertir en string pour éviter les erreurs et nettoyer les caractères non numériques
        df["Prix"] = df["Prix"].astype(str).apply(lambda x: re.sub(r"\D", "", x) if re.sub(r"\D", "", x) else None)

        # Convertir en entier (gérer les NaN)
        df["Prix"] = pd.to_numeric(df["Prix"], errors="coerce")

        # Remplacer les NaN par la moyenne des prix existants
        mean_price = df["Prix"].mean()
        df["Prix"].fillna(mean_price, inplace=True)

        # Convertir en entier final pour éviter les décimales
        df["Prix"] = df["Prix"].astype(int)
    df["Localisation"] = df["Localisation"].str.title()
    df["Localisation"] = df["Localisation"].replace(["N/A", "Inconnu", "Non Spécifié"], "Non Renseigné")
    df.drop_duplicates(inplace=True)
    df = df[df["Détails"].str.len() > 5]
    return df

# Interface utilisateur Streamlit avec onglets
st.markdown("<h1 style='text-align: center; color: black;'>MY DATA APP</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Scraping", "📈 Dashboard", "🌐 WebScraper Data"])

# Onglet Scraping
with tab1:
    st.sidebar.header("Options de Scraping")
    selected_category = st.sidebar.selectbox("Choisir une catégorie :", ["Toutes les catégories"] + list(URLS.keys()))
    num_pages = st.sidebar.number_input("Nombre de pages à scraper", min_value=1, max_value=50, value=2, step=1)
    clean_data_option = st.sidebar.checkbox("Nettoyer les données avant affichage", value=True)

    def load_existing_data():
        """Charger et afficher les données existantes dans les fichiers CSV."""
        if selected_category == "Toutes les catégories":
            for category in URLS.keys():
                file_path = f"data/{category.lower().replace(' ', '_')}.csv"
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

    # Charger les données existantes dès l'ouverture de l'onglet
    load_existing_data()

    # Bouton de scraping
    if st.sidebar.button("Scraper les données"):
        st.sidebar.success(f"Lancement du scraping pour {selected_category} ({num_pages} pages)...")
        progress_bar = st.progress(0)

        if selected_category == "Toutes les catégories":
            total_categories = len(URLS)
            for idx, (category, url) in enumerate(URLS.items(), start=1):
                st.markdown(f"### 🔄 Scraping des **{category}**...")
                data = scrap_data(url, max_pages=num_pages)
                df = pd.DataFrame(data)
                if clean_data_option:
                    df = clean_data(df)
                file_path = f"data/{category.lower().replace(' ', '_')}.csv"
                df.to_csv(file_path, index=False, encoding='utf-8')
                st.sidebar.success(f"✅ {category} terminé !")
                st.markdown(f"### 📊 Données des {category}")
                st.dataframe(df)
                progress_bar.progress(int((idx / total_categories) * 100))

        else:
            st.markdown(f"### 🔄 Scraping des **{selected_category}**...")
            data = scrap_data(URLS[selected_category], max_pages=num_pages)
            df = pd.DataFrame(data)
            if clean_data_option:
                df = clean_data(df)
            file_path = f"data/{selected_category.lower().replace(' ', '_')}.csv"
            df.to_csv(file_path, index=False, encoding='utf-8')
            st.sidebar.success(f"✅ {selected_category} terminé !")
            st.markdown(f"### 📊 Données des {selected_category}")
            st.dataframe(df)
            progress_bar.progress(100)

        st.sidebar.success("🎉 Scraping terminé avec succès !")

# Onglet Dashboard
with tab2:
    st.markdown("## 📈 Dashboard des données scrappées")
    selected_dashboard_category = st.selectbox("Choisir une catégorie à analyser :", list(URLS.keys()))

    file_path = f"data/{selected_dashboard_category.lower().replace(' ', '_')}.csv"
    try:
        df_dashboard = pd.read_csv(file_path)

        # Nettoyage des données
        df_dashboard["Prix"] = pd.to_numeric(df_dashboard["Prix"], errors="coerce").fillna(0)
        df_dashboard["Localisation"] = df_dashboard["Localisation"].fillna("Non renseigné")

        # 1️⃣ Distribution des prix
        st.markdown("### 📊 Distribution des prix")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(df_dashboard["Prix"], bins=30, kde=True, color="blue")
        plt.xlabel("Prix (FCFA)")
        plt.ylabel("Nombre d'annonces")
        st.pyplot(fig)

        # 2️⃣ Localisations les plus fréquentes
        st.markdown("### 📍 Localisations les plus fréquentes")
        top_locations = df_dashboard["Localisation"].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x=top_locations.values, y=top_locations.index, palette="viridis")
        plt.xlabel("Nombre d'annonces")
        plt.ylabel("Localisation")
        st.pyplot(fig)

        # 3️⃣ Boxplot des prix par catégorie
        st.markdown("### 💰 Comparaison du prix des annonces")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.boxplot(y=df_dashboard["Prix"], color="orange")
        plt.ylabel("Prix (FCFA)")
        st.pyplot(fig)

        # 4️⃣ Histogramme du nombre d’annonces par tranche de prix
        st.markdown("### 📌 Répartition des annonces par gamme de prix")
        price_bins = [0, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000]
        labels = ["<100K", "100K-500K", "500K-1M", "1M-5M", "5M-10M", "10M-50M", "50M+"]
        df_dashboard["Tranche de prix"] = pd.cut(df_dashboard["Prix"], bins=price_bins, labels=labels)

        fig, ax = plt.subplots(figsize=(8, 4))
        sns.countplot(y=df_dashboard["Tranche de prix"], order=labels, palette="coolwarm")
        plt.xlabel("Nombre d'annonces")
        plt.ylabel("Tranche de prix")
        st.pyplot(fig)

    except FileNotFoundError:
        st.warning(f"⚠️ Aucune donnée trouvée pour {selected_dashboard_category}. Veuillez scraper d'abord.")

# Onglet WebScraper Data
with tab3:
    st.markdown("## 🌐 Données WebScraper")
    st.write("Cette section affiche les données scrapées avec WebScraper.")

    # Charger les données WebScraper
    webscraper_file = st.file_uploader("Téléverser un fichier WebScraper (CSV ou JSON)", type=["csv", "json"])
    if webscraper_file is not None:
        try:
            if webscraper_file.name.endswith(".csv"):
                df_webscraper = pd.read_csv(webscraper_file)
            elif webscraper_file.name.endswith(".json"):
                df_webscraper = pd.read_json(webscraper_file)
            else:
                st.error("Format de fichier non supporté. Veuillez téléverser un fichier CSV ou JSON.")
                st.stop()

            st.markdown("### 📊 Données WebScraper")
            st.dataframe(df_webscraper)

            # Visualisations supplémentaires (optionnelles)
            if "price" in df_webscraper.columns:
                st.markdown("### 📊 Distribution des prix (WebScraper)")
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.histplot(df_webscraper["price"], bins=30, kde=True, color="green")
                plt.xlabel("Prix")
                plt.ylabel("Nombre d'annonces")
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {e}")
    else:
        st.info("Veuillez téléverser un fichier pour afficher les données WebScraper.")