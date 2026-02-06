import streamlit as st
import requests
import pandas as pd
import streamlit as st
import pandas as pd
import requests
import xmltodict
import urllib3
import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit as st
import pandas as pd
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
import warnings
import pandas as pd
import logging

import pandas as pd
from utils import  fonctions, scrap
from IPython.display import display
import streamlit as st
import pandas as pd
import requests
import pandas as pd
import numpy as np
from googleapiclient.discovery import build
import urllib3
import xmltodict
import nltk
nltk.download('stopwords')  # Télécharger les stopwords avant de les utiliser
from nltk.corpus import stopwords
stop_words = set(stopwords.words("french"))

# Dates
from datetime import date, datetime, timedelta, time
# Fonction de login
def login_page():
    st.title("Page de Login")

    # Vérifier si l'utilisateur est déjà connecté
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.success("Vous êtes déjà connecté!")
        # Si connecté, ouvrir directement la page de gestion des flux
        st.session_state.page = "audit"  # Change the page state to 'audit'
        audit_page()  # Directly call the audit page
    else:
        # Demander à l'utilisateur de saisir son nom d'utilisateur et son mot de passe
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if username == "admin" and password == "password123":
                # Définir l'état de la session comme connecté
                st.session_state["logged_in"] = True
                st.session_state["page"] = "audit"  # Set the page to 'audit' to simulate rerun behavior
                st.success("Connexion réussie!")
                # Effectuer un rerun pour que l'état de la session prenne effet
                st.rerun()  # Forcer le rerun de l'application pour afficher la page d'audit
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

# Fonction de gestion des flux (audit_page)
def audit_page():
    st.title("Feed Management")

    # Champ de saisie pour l'URL du flux
    uploaded_file = st.file_uploader("Téléchargez un fichier CSV", type=["csv"])

    # Bouton Valider
    if st.button("Valider"):
        # Une fois que l'utilisateur clique sur Valider, on procède au traitement
        if uploaded_file:

            try:
                # Charger les données depuis le fichier CSV
                st.info("Chargement et traitement du fichier CSV. Veuillez patienter...")
                df_data = pd.read_csv(uploaded_file, sep = ';')

                # Afficher les résultats
                st.success("Traitement terminé ! Voici vos résultats :")

                # Afficher les données brutes
                st.subheader("Aperçu des données brutes")
                st.dataframe(df_data)

                # Afficher la liste des concurrents
                st.subheader("Vos concurrents")
                concurrents = traitement(df_data)[0]
                st.dataframe(concurrents)

                # Bouton de téléchargement
                csv = concurrents.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Télécharger les résultats en CSV",
                    data=csv,
                    file_name='concurrents.csv',
                    mime='text/csv',
                    key='download_concurrents_button'  # Clé unique

                )

                # Afficher le scrap des concurrents
                st.subheader("Contenu de la page des concurrents")
                scrap_concurrents = traitement(df_data)[1]
                st.dataframe(scrap_concurrents)

                # Bouton de téléchargement
                csv = scrap_concurrents.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Télécharger les résultats en CSV",
                    data=csv,
                    file_name='scrap_concurrents.csv',
                    mime='text/csv',
                    key='download_scrap_button'  # Clé unique

                )

                # Afficher les recommandations
                st.subheader("Contenu de la page des concurrents")
                recommandations= traitement(df_data)[1]
                st.dataframe(recommandations)

                # Bouton de téléchargement
                csv = recommandations.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Télécharger les résultats en CSV",
                    data=csv,
                    file_name='recommandations.csv',
                    mime='text/csv',
                    key='download_recommandations_button'  # Clé unique

                )

            except requests.exceptions.RequestException as e:
                st.error(f"Failed to fetch the data from the provided URL: {e}")
            except pd.errors.ParserError as e:
                st.error(f"Failed to parse the data: {e}")
        else:
            # Si l'utilisateur n'a pas rempli les deux champs
            st.error("Veuillez remplir les deux sections avant de cliquer sur Valider.")

def traitement(data):
    keywords = data['keywords']
    search_engine = data['search_engine']

    df_serpapi = fonctions.process_serpapi_data(keywords, search_engine)
    #display(df_serpapi.sample(10))
    df_serpapi_export = df_serpapi.astype(str)
    #ggsheet.googleSheetExport(client['url_export_serpapi'], df_serpapi_export)
    # Exemple d'utilisation
    urls_to_analyze = df_serpapi_export['url'].tolist()
    companies = df_serpapi_export['company'].tolist()
    search_terms = df_serpapi_export['Search term'].tolist()
    df_scrap = scrap.analyze_multiple_pages(urls_to_analyze,companies, search_terms)
    #ggsheet.googleSheetExport(client['url_scrap'], df_scrap)
    return df_serpapi_export, df_scrap


# Fonction pour importer et traiter les flux XML
def XMLImport(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    data = xmltodict.parse(response.data)
    list_champs = []
    for i in data['rss']['channel']['item']:
        list_champs.extend(list(i.keys()))
    df = pd.DataFrame()
    for ele in set(list_champs):
        df[ele] = [i[ele] if ele in i.keys() else '' for i in data['rss']['channel']['item']]
    return df

# Démarrer l'application
if __name__ == "__main__":
    # Vérifier si l'utilisateur est connecté et gérer les pages
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        # Si l'utilisateur est déjà connecté, afficher directement la page d'audit
        audit_page()
    else:
        # Sinon, afficher la page de login
        login_page()
