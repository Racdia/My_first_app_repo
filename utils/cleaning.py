import pandas as pd
import re
import streamlit as st
import plotly.express as px

def clean_data(df):
    df = df.copy()

    if "prix" in df.columns:
        df["prix"] = df["prix"].astype(str)

        df["prix"] = df["prix"].replace("Prix sur demande", None)

        df["prix"] = df["prix"].apply(lambda x: re.sub(r"[^\d]", "", x) if isinstance(x, str) else x)

        df["prix"] = pd.to_numeric(df["prix"], errors="coerce")

        if df["prix"].notna().sum() > 0:
            mean_price = df["prix"].mean(skipna=True)
            df["prix"].fillna(mean_price, inplace=True)

        df["prix"] = df["prix"].astype(int)

    if "adresse" in df.columns:
        df["adresse"] = df["adresse"].astype(str).str.strip()
        df["adresse"] = df["adresse"].replace(["N/A", "Inconnu", "Non Spécifié"], "Non Renseigné")


        df["adresse"] = df["adresse"].str.replace("location_on", "", regex=False).str.strip()


    df.drop_duplicates(inplace=True)


    print(df.info())
    print(df.head())

    return df
