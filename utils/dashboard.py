import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.cleaning import clean_data


def display_dashboard(df, category):
    st.subheader(f"📊 Analyse des données pour {category}")

    df = clean_data(df)  # Appliquer le nettoyage

    # ✅ Assurer la normalisation des noms de colonnes
    df.columns = df.columns.str.lower()

    if "prix" not in df.columns or df.empty:
        st.warning("⚠️ Aucune donnée valide pour afficher le dashboard.")
        return

    # ✅ Statistiques générales
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Nombre d'annonces", len(df))
    df = df[df["prix"] < 10_000_000]
    prix_moyen = df["prix"].mean()
    prix_max = df["prix"].max()

    col2.metric("💰 Prix Moyen", f"{prix_moyen:,.0f} FCFA".replace(",", " "))
    col3.metric("🔝 Prix Max", f"{prix_max:,.0f} FCFA".replace(",", " "))

    # ✅ Histogramme de la distribution des prix
    st.markdown("### 💲 Distribution des Prix")
    fig = px.histogram(df, x="prix", nbins=30, title="Distribution des prix", color_discrete_sequence=["blue"])
    st.plotly_chart(fig, use_container_width=True)

    # ✅ Localisations les plus fréquentes
    st.markdown("### 📍 Top 10 Localisations")
    if "adresse" in df.columns:
        top_locations = df["adresse"].value_counts().head(10).reset_index()
        top_locations.columns = ["adresse", "Nombre d'annonces"]

        fig = px.bar(top_locations, x="Nombre d'annonces", y="adresse", orientation="h",
                     title="Top Localisations", color="Nombre d'annonces", color_continuous_scale="viridis")
        st.plotly_chart(fig, use_container_width=True)

    # ✅ Moyenne des prix par localisation
    st.markdown("### 💵 Moyenne des prix par Localisation")
    if "adresse" in df.columns:
        location_price_avg = df.groupby("adresse")["prix"].mean().reset_index()
        location_price_avg = location_price_avg.sort_values(by="prix", ascending=False).head(10)

        fig = px.bar(location_price_avg, x="adresse", y="prix",
                     title="Moyenne des prix par Localisation",
                     color="prix", color_continuous_scale="blues")
        st.plotly_chart(fig, use_container_width=True)

    # ✅ Top 5 des annonces les plus chères
    st.markdown("### 🔝 Top 5 des annonces les plus chères")
    top_expensive = df.nlargest(5, "prix")[["adresse", "prix"]]

    fig = px.bar(top_expensive, x="adresse", y="prix",
                 title="Top 5 des annonces les plus chères",
                 color="prix", color_continuous_scale="reds")
    st.plotly_chart(fig, use_container_width=True)

