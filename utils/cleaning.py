import pandas as pd
import re
import streamlit as st
import plotly.express as px

def clean_data(df):
    df = df.copy()  # Éviter de modifier le DataFrame d'origine directement

    # ✅ Nettoyage de la colonne "prix"
    if "prix" in df.columns:
        df["prix"] = df["prix"].astype(str)  # Convertir en chaîne pour éviter les erreurs

        # Supprimer "Prix sur demande" et remplacer les valeurs textuelles par None
        df["prix"] = df["prix"].replace("Prix sur demande", None)

        # Supprimer "CFA", espaces et autres caractères non numériques
        df["prix"] = df["prix"].apply(lambda x: re.sub(r"[^\d]", "", x) if isinstance(x, str) else x)

        # Convertir en numérique
        df["prix"] = pd.to_numeric(df["prix"], errors="coerce")

        # Si tous les prix sont NaN, on ne remplace pas pour éviter un DF vide
        if df["prix"].notna().sum() > 0:
            mean_price = df["prix"].mean(skipna=True)
            df["prix"].fillna(mean_price, inplace=True)

        df["prix"] = df["prix"].astype(int)  # Convertir en entier

    # ✅ Nettoyage de la colonne "adresse"
    if "adresse" in df.columns:
        df["adresse"] = df["adresse"].astype(str).str.strip()
        df["adresse"] = df["adresse"].replace(["N/A", "Inconnu", "Non Spécifié"], "Non Renseigné")

        # Supprimer "location_on"
        df["adresse"] = df["adresse"].str.replace("location_on", "", regex=False).str.strip()

    # ✅ Suppression des doublons
    df.drop_duplicates(inplace=True)

    # ✅ Vérification finale
    print(df.info())  # Vérifier s'il reste des données
    print(df.head())  # Afficher les 5 premières lignes

    return df
