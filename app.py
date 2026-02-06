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
# Dates
from datetime import date, datetime, timedelta, time
import asyncio
import nest_asyncio

# Configurer une boucle d'événements si elle n'existe pas
try:
    asyncio.get_running_loop()
except RuntimeError:  # Si aucune boucle n'est active
    asyncio.set_event_loop(asyncio.new_event_loop())

nest_asyncio.apply()



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

warnings.filterwarnings('ignore')

url_login_info = 'https://docs.google.com/spreadsheets/d/1XwQZwNXHfmmpQU7tcGhB2MWCAoQj1vi3BcL2Q2mOwlM/edit?gid=0#gid=0'
url_cat_advice = 'https://docs.google.com/spreadsheets/d/13Ujrp1d3FHcRxTQLRUjkRKqJrgujYAeeq2wrFvjDZPY/edit?gid=2045289059#gid=2045289059'
url_postlist = "https://www.meetic.fr/p/lists/postList.json"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
max_index = 0

def save_session_to_firestore():
    """
    Saves the session data from st.session_state to Firestore.
    """
    if 'user_state' in st.session_state and st.session_state.user_state.get('logged_in', False):
        user_data = st.session_state.user_state
        username = user_data['username']
        session_id = user_data['session_id']
        
        # Reference to the main user document by username
        user_doc_ref = db.collection("sessions").document(username)
        
        # Save general user information in the main document if it doesn’t exist
        user_doc_ref.set({
            "username": username,
            "last_login": datetime.now().isoformat()
        }, merge=True)
        
        # Reference to the specific session document in a subcollection
        session_doc_ref = user_doc_ref.collection("user_sessions").document(f"{username}_{session_id}")
        
        # Save the session data, including interactions, to the subcollection
        session_doc_ref.set({
            "session_id": session_id,
            "username": username,
            "login_time": user_data.get("login_time", datetime.now().isoformat()),
            "interactions": user_data.get("interactions", [])
        })
        
        print(f"Session data for {username} saved to Firestore")


def XMLImport(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    data = xmltodict.parse(response.data)
    list_champs = []
    for i in data['rss']['channel']['item'] :
        list_champs.extend(list(i.keys()))
    df = pd.DataFrame()
    for ele in set(list_champs) :
        df[ele] = [i[ele] if ele in i.keys() else '' for i in data['rss']['channel']['item']]
    return df


def audit_page_old():
    st.title("Feed Management")

    # Input field for the feed URL
    feed_url = st.text_input("Enter the URL of the feed:")

    if feed_url:
        try:
            # Fetch data from the URL
            response = requests.get(feed_url)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

            # Load the data into a DataFrame
            #df_flux = pd.read_csv(pd.compat.StringIO(response.text), sep=',')

            df_flux = XMLImport(response.text)
    
            try:
                df_flux.rename(columns={'g:id': 'id'}, inplace=True)  
                df_flux.rename(columns={'g:image_link': 'image_link'}, inplace=True)  
                df_flux.rename(columns={'g:product_type': 'product_type'}, inplace=True)  
                df_flux.rename(columns={'g:brand': 'brand'}, inplace=True)  
            except:
                pass 
            
            df_flux = df_flux.head(10)

            # Process the data
            df_flux['new_title'] = df_flux.apply(
                calculate.generate_new_title, axis=1, args=('FR',)
            )
            df_title = df_flux[['id', 'new_title', 'title', 'brand']]

            # Clean the 'new_title' column
            df_title['new_title'] = (
                df_title['new_title']
                .str.replace(' beauty', '', case=False)
                .str.replace('"', '', case=False)
            )

            # Display the processed data
            st.subheader("Final Results")
            st.dataframe(df_title)

            # Convert the DataFrame to CSV format for download
            csv = df_title.to_csv(index=False).encode('utf-8')

            # Provide download button for the processed CSV
            st.download_button(
                label="Download Processed CSV",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv",
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch the data from the provided URL: {e}")
        except pd.errors.ParserError as e:
            st.error(f"Failed to parse the CSV data: {e}")





def log_global_error_to_firestore(error_message, username=None):
    """
    Logs an error message to Firestore under the user's errors subcollection or a global errors collection.
    """
    # db = firestore.Client()  # Assumes global Firestore client if initialized elsewhere
    
    # If a username is provided, log to the user's errors subcollection
    if username:
        errors_doc_ref = db.collection("sessions").document(username).collection("errors").document()
    else:
        # Log to a global errors collection if no username is available
        errors_doc_ref = db.collection("global_errors").document()

    # Log the error with a timestamp
    errors_doc_ref.set({
        "timestamp": datetime.now().isoformat(),
        "error_message": error_message
    })


import streamlit as st
import requests
import pandas as pd

import streamlit as st
import pandas as pd
import requests
import xmltodict
import urllib3

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
                df_data = pd.read_csv(uploaded_file)

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
                    file_name='concurrents.csv',
                    mime='text/csv',
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
                    file_name='concurrents.csv',
                    mime='text/csv',
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
