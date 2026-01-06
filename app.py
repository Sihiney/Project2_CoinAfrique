import streamlit as st
from src.scraping_bs4 import scrape_coinafrique
import os
import pandas as pd
# -----------------------------
# Config
# -----------------------------
st.set_page_config(
    page_title="CoinAfrique – Mini projet Data Collection",
    layout="wide"
)

# -----------------------------
# Titre
# -----------------------------
st.title("CoinAfrique – Mini projet 2 Data Collection")
st.write(
    """
    Cette application a été développée dans le cadre du cours de Data Collection.
    Elle permet de collecter, explorer et analyser des données issues du site CoinAfrique
    en utilisant différentes approches.
    """
)

st.markdown("---")

# -----------------------------
# Sidebar – Navigation
# -----------------------------
st.sidebar.title("Menu")

option = st.sidebar.radio(
    "Choisissez une option :",
    (
        "1. Scraper avec BeautifulSoup",
        "2. Télécharger données WebScraper (brutes)",
        "3. Dashboard (données nettoyées)",
        "4. Évaluer l’application"
    )
)

# -----------------------------
# Option 1 – Scraping BeautifulSoup 
# -----------------------------
if option == "1. Scraper avec BeautifulSoup":
    st.header("Scraping avec BeautifulSoup")

    categorie_label = st.selectbox(
        "Choisissez une catégorie",
        ["Vêtements homme", "Chaussures homme", "Vêtements enfants", "Chaussures enfants"]
    )

    category_key_map = {
        "Vêtements homme": "vetements_homme",
        "Chaussures homme": "chaussures_homme",
        "Vêtements enfants": "vetements_enfants",
        "Chaussures enfants": "chaussures_enfants",
    }
    category_key = category_key_map[categorie_label]

    nb_pages = st.number_input("Nombre de pages à scraper", min_value=1, max_value=50, value=2)

    if st.button("Lancer le scraping"):
        with st.spinner("Scraping en cours..."):
            df = scrape_coinafrique(category_key, nb_pages)

        st.success(f"Scraping terminé. Lignes récupérées: {len(df)}")
        st.dataframe(df)

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Télécharger le CSV",
            data=csv_bytes,
            file_name=f"coinafrique_bs4_{category_key}_pages_{nb_pages}.csv",
            mime="text/csv"
        )

# -----------------------------
# Option 2 – Données WebScraper brutes
# -----------------------------
elif option == "2. Télécharger données WebScraper (brutes)":
    st.header("Données WebScraper – version brute")

    st.write(
        "Cette section permet de télécharger des données déjà scrapées avec WebScraper.io. "
        "Les données sont brutes (non nettoyées)."
    )

    RAW_DIR = os.path.join("data", "brut", "webscraper")

    files_map = {
        "Vêtements homme (brut)": "coinafrique_vetements_homme.csv",
        "Chaussures homme (brut)": "coinafrique_chaussures-homme.csv",
        "Vêtements enfants (brut)": "coinafrique_vetements_enfants.csv",
        "Chaussures enfants (brut)": "coinafrique_chaussures-enfants.csv",
    }

    choix = st.selectbox("Choisissez un fichier brut", list(files_map.keys()))
    selected_file = files_map[choix]
    path = os.path.join(RAW_DIR, selected_file)

    if not os.path.exists(path):
        st.error(f"Fichier introuvable: {path}")
    else:
        df_raw = pd.read_csv(path)
        st.write(f"Fichier: `{selected_file}`")
        st.write(f"Lignes: {len(df_raw)} | Colonnes: {len(df_raw.columns)}")
        st.dataframe(df_raw.head(50))

        csv_bytes = df_raw.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Télécharger le CSV brut",
            data=csv_bytes,
            file_name=selected_file,
            mime="text/csv"
        )

# -----------------------------
# Option 3 – Dashboard
# -----------------------------
elif option == "3. Dashboard (données nettoyées)":
    import os
    import pandas as pd
    import matplotlib.pyplot as plt
    import streamlit as st

    st.header("Dashboard – Données nettoyées")

    CLEAN_PATH = os.path.join("data", "nettoye", "coinafrique_all_clean.csv")

    if not os.path.exists(CLEAN_PATH):
        st.error(f"Fichier introuvable : {CLEAN_PATH}")
    else:
        df = pd.read_csv(CLEAN_PATH)

        # -----------------------------
        # Filtres
        # -----------------------------
        st.subheader("Filtres")

        if "categorie" in df.columns:
            categories = sorted(df["categorie"].dropna().unique().tolist())
            selected_categories = st.multiselect(
                "Catégories",
                options=categories,
                default=categories
            )
            dff = df[df["categorie"].isin(selected_categories)]
        else:
            dff = df.copy()

        st.markdown("---")

        # -----------------------------
        # Indicateurs
        # -----------------------------
        st.subheader("Indicateurs")

        total_ads = len(dff)
        loc_unique = dff["adresse"].nunique() if "adresse" in dff.columns else 0

        c1, c2 = st.columns(2)
        c1.metric("Annonces", total_ads)
        c2.metric("Localisations", loc_unique)

        st.markdown("---")

        # -----------------------------
        # Graphique 1 : Annonces par catégorie
        # -----------------------------
        st.subheader("Annonces par catégorie")

        if "categorie" in dff.columns:
            fig1, ax1 = plt.subplots()
            dff["categorie"].value_counts().plot(kind="bar", ax=ax1)
            ax1.set_xlabel("Catégorie")
            ax1.set_ylabel("Nombre d'annonces")
            ax1.set_title("Nombre d'annonces par catégorie")
            st.pyplot(fig1)
        else:
            st.info("Colonne categorie introuvable.")

        # -----------------------------
        # Graphique 2 : Top 10 localisations
        # -----------------------------
        st.subheader("Top 10 localisations")

        if "adresse" in dff.columns:
            top_loc = dff["adresse"].value_counts().head(10)
            fig2, ax2 = plt.subplots()
            top_loc.sort_values().plot(kind="barh", ax=ax2)
            ax2.set_xlabel("Nombre d'annonces")
            ax2.set_ylabel("Localisation")
            ax2.set_title("Top 10 des localisations")
            st.pyplot(fig2)
        else:
            st.info("Colonne adresse introuvable.")

        st.markdown("---")

        # -----------------------------
        # Aperçu
        # -----------------------------
        st.subheader("Aperçu des données")
        st.dataframe(dff.head(50))

# -----------------------------
# Option 4 – Évaluation
# -----------------------------
elif option == "4. Évaluer l’application":
    import streamlit as st

    st.header("Évaluer l’application")

    st.write(
        "Merci de prendre quelques minutes pour évaluer cette application. "
        "Choisissez l’un des formulaires ci-dessous."
    )

    # Remplace ces liens par tes vrais liens
    KOBO_URL = "https://ee.kobotoolbox.org/x/JD4VOK4y"
    GOOGLE_FORMS_URL = "a completer si j'ai le temps"

    col1, col2 = st.columns(2)

    with col1:
        st.link_button("Ouvrir le formulaire Kobo", KOBO_URL)

    with col2:
        st.link_button("Ouvrir le formulaire Google Forms", GOOGLE_FORMS_URL)

    st.caption(
        "Note: le formulaire Google Forms ne contient pas la partie avec calcul."
    )