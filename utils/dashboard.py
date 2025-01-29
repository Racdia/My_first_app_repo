import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def display_dashboard(df, category):
    st.subheader(f"📊 Analyse des données pour {category}")
    df.columns = df.columns.str.lower()

    # 🔹 Normalisation des noms de colonnes
    df["prix"] = df["prix"].replace({'FCFA': '', ',': ''}, regex=True)

    # Conversion de la colonne 'prix' en type numérique (float)
    df["prix"] = pd.to_numeric(df["prix"], errors='coerce')

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Nombre d'annonces", len(df))

    if "prix" in df.columns and not df["prix"].empty:
        prix_moyen = df["prix"].mean()
        prix_max = df["prix"].max()
    else:
        prix_moyen = 0
        prix_max = 0

    col2.metric("💰 Prix Moyen", f"{float(prix_moyen):,.2f} FCFA")  # Formatage avec 2 décimales
    col3.metric("🔝 Prix Max", f"{float(prix_max):,.2f} FCFA")  # Formatage avec 2 décimales

    # 📊 Histogramme de la distribution des prix
    st.markdown("### 💲 Distribution des Prix")
    fig = px.histogram(df, x="prix", nbins=30, title="Distribution des prix", color_discrete_sequence=["blue"])
    st.plotly_chart(fig, use_container_width=True)

    # 🔝 Localisations les plus fréquentes
    st.markdown("### 📍 Top 10 Localisations")
    if "localisation" in df.columns:
        top_locations = df["localisation"].value_counts().head(10).reset_index()
        top_locations.columns = ["Localisation", "Nombre d'annonces"]

        fig = px.bar(top_locations, x="Nombre d'annonces", y="Localisation", orientation="h",
                     title="Top Localisations", color="Nombre d'annonces", color_continuous_scale="viridis")
        st.plotly_chart(fig, use_container_width=True)

    # 📉 Tendance des prix au fil du temps
    if "date" in df.columns:
        df_date = df.copy()  # Éviter de modifier l'original
        df_date["date"] = pd.to_datetime(df_date["date"], errors="coerce")
        df_date = df_date.dropna(subset=["date"])
        df_date = df_date.sort_values(by="date")

        if not df_date.empty:  # Vérifier qu'il y a bien des données
            st.markdown("### 📅 Évolution des prix")
            fig = px.line(df_date, x="date", y="prix", title="Tendance des prix au fil du temps", markers=True)
            st.plotly_chart(fig, use_container_width=True)



    # 📊 Moyenne des prix par localisation - Bar Chart
    st.markdown("### 💵 Moyenne des prix par Localisation")
    if "localisation" in df.columns and "prix" in df.columns:
        location_price_avg = df.groupby("localisation")["prix"].mean().reset_index()
        location_price_avg = location_price_avg.sort_values(by="prix", ascending=False).head(10)

        fig = px.bar(location_price_avg, x="localisation", y="prix",
                     title="Moyenne des prix par Localisation",
                     color="prix", color_continuous_scale="blues")
        st.plotly_chart(fig, use_container_width=True)

    # 📈 Top 5 des annonces avec les prix les plus élevés - Bar Chart
    st.markdown("### 🔝 Top 5 des annonces les plus chères")
    if "localisation" in df.columns and "prix" in df.columns:
        top_expensive = df.nlargest(5, "prix")[["localisation", "prix"]]

        fig = px.bar(top_expensive, x="localisation", y="prix",
                     title="Top 5 des annonces les plus chères",
                     color="prix", color_continuous_scale="reds")
        st.plotly_chart(fig, use_container_width=True)
