import pandas as pd
import re


def clean_data(df):
    df = df.copy()  # Éviter de modifier le DataFrame d'origine

    # Nettoyage de la colonne "prix"
    if "prix" in df.columns:
        df["prix"] = df["prix"].astype(str).apply(lambda x: re.sub(r"\D", "", x) if isinstance(x, str) else x)  # Supprime tout sauf les chiffres
        df["prix"] = pd.to_numeric(df["prix"], errors="coerce")  # Convertit en numérique (float)

        if df["prix"].notna().sum() > 0:  # Vérifier si la colonne contient des valeurs
            mean_price = df["prix"].mean()
            df["prix"].fillna(mean_price, inplace=True)

            # Vérifier si la conversion en int est possible
            if df["prix"].notna().sum() > 0:
                df["prix"] = df["prix"].astype(int)
            else:
                df["prix"] = 0  # Si toutes les valeurs sont NaN

    # Nettoyage de la colonne "localisation"
    if "localisation" in df.columns:
        df["localisation"] = df["localisation"].astype(str).str.strip().replace(["N/A", "Inconnu", "Non Spécifié"], "Non Renseigné")
        df["localisation"] = df["localisation"].apply(lambda x: x.capitalize() if isinstance(x, str) else x)

    # Suppression des doublons
    df.drop_duplicates(inplace=True)

    # Nettoyage de la colonne "Détails"
    if "Détails" in df.columns:
        df["Détails"] = df["Détails"].astype(str)  # Convertir en string pour éviter les erreurs
        df = df[df["Détails"].str.len() > 5]  # Filtrer uniquement les descriptions longues

    return df
