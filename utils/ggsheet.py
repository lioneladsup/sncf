# General imports
import pandas as pd
import re, json
import socket
from utils import secrets

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Librairies Google
from googleapiclient.discovery import build
from google.oauth2 import service_account

########## Credentials ##########
service_account_info_str = secrets.access_secret(secret_id = 'projects/318987655175/secrets/keysMCCSheet')
service_account_info = json.loads(service_account_info_str)
creds = service_account.Credentials.from_service_account_info(service_account_info)

# Modifier le timeout limit
timeout_in_sec = 60*5 # timeout limit de 5 min
socket.setdefaulttimeout(timeout_in_sec)

########## Fonctions ##########
@retry(
    stop = stop_after_attempt(5),
    wait = wait_exponential(multiplier = 2, min = 1, max = 20),
    retry = retry_if_exception_type(Exception)
)
def googleSheetImport(url):
    try:
        global erreur
        x = url
        id_gsheet = re.search('d\/([a-zA-Z0-9_-]+)', x).group(1)
        gid_gsheet = re.search('gid=([a-zA-Z0-9_-]+)', x).group(1)

        # Call Sheets API
        service = build('sheets', 'v4', credentials = creds)
        sheet = service.spreadsheets()

        # Call Sheets API
        service = build('sheets', 'v4', credentials = creds)
        sheet_metadata = service.spreadsheets().get(spreadsheetId = id_gsheet).execute()
        sheets = sheet_metadata.get('sheets', '')

        # boucle sur les pages du google sheet pour récupérer l'id de page
        for i in sheets :
            title = i['properties']['title']
            sheet_id = i['properties']['sheetId']
            # si l'id de la feuille est celle demandée
            if gid_gsheet == str(sheet_id) :
                # Obtenir les valeurs du Google Sheet
                result = sheet.values().get(spreadsheetId = id_gsheet, range = title).execute()
                values = result.get('values')
                return pd.DataFrame(columns = values[0], data = values[1:len(values)])
            # si l'id de la feuille n'est pas celle demandée
            else :
                pass
    except Exception as e:
        print(f"Erreur lors de l'import de Google Sheet : {e}")
        raise


@retry(
    stop = stop_after_attempt(5),
    wait = wait_exponential(multiplier = 2, min = 1, max = 20),
    retry = retry_if_exception_type(Exception)
)
def googleSheetExport(url, df):
    try:
        # Passer du dataframe au format adequat pour l'export sur googlesheet
        produit = df
        produit = produit.fillna('')
        Data = []
        Weight = produit.values.tolist()
        ColumnName = produit.keys().tolist()
        Data.append(ColumnName)
        for i in Weight :
            Data.append(i)

        # Format de l'url
        x = url

        id_gsheet = re.search('d\/([a-zA-Z0-9_-]+)', x).group(1)
        gid_gsheet = re.search('gid=([a-zA-Z0-9_-]+)', x).group(1)

        # Call Sheets API
        service = build('sheets', 'v4', credentials = creds)
        sheet = service.spreadsheets()
        sheet_metadata = service.spreadsheets().get(spreadsheetId = id_gsheet).execute()
        sheets = sheet_metadata.get('sheets', '')

        # boucle sur les pages du google sheet pour récupérer l'id de page
        for i in sheets :
            title = i['properties']['title']
            sheet_id = i['properties']['sheetId']
            if gid_gsheet == str(sheet_id) :
                NAME_PAGE = title

                # Supprimer les données présentes avant l'export
                clear = sheet.values().clear(spreadsheetId = id_gsheet, range = NAME_PAGE).execute()

                # Exporter les données dans le Google Sheet
                request = sheet.values().update(
                    spreadsheetId = id_gsheet,
                    range = NAME_PAGE,
                    valueInputOption = 'USER_ENTERED',
                    body = {'values' : Data}
                    ).execute()
            else :
                1
    except Exception as e:
        print(f"Erreur lors de l'export de Google Sheet : {e}")
        raise


# General imports
import pandas as pd
import re, json
import socket
from utils import secrets

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Librairies Google
from googleapiclient.discovery import build
from google.oauth2 import service_account

########## Credentials ##########
service_account_info_str = secrets.access_secret(secret_id = 'projects/318987655175/secrets/keysMCCSheet')
service_account_info = json.loads(service_account_info_str)
creds = service_account.Credentials.from_service_account_info(service_account_info)

# Modifier le timeout limit
timeout_in_sec = 60*5 # timeout limit de 5 min
socket.setdefaulttimeout(timeout_in_sec)

########## Fonctions ##########
@retry(
    stop = stop_after_attempt(5),
    wait = wait_exponential(multiplier = 2, min = 1, max = 20),
    retry = retry_if_exception_type(Exception)
)
def googleSheetImport(url):
    try:
        global erreur
        x = url
        id_gsheet = re.search('d\/([a-zA-Z0-9_-]+)', x).group(1)
        gid_gsheet = re.search('gid=([a-zA-Z0-9_-]+)', x).group(1)

        # Call Sheets API
        service = build('sheets', 'v4', credentials = creds)
        sheet = service.spreadsheets()

        # Call Sheets API
        service = build('sheets', 'v4', credentials = creds)
        sheet_metadata = service.spreadsheets().get(spreadsheetId = id_gsheet).execute()
        sheets = sheet_metadata.get('sheets', '')

        # boucle sur les pages du google sheet pour récupérer l'id de page
        for i in sheets :
            title = i['properties']['title']
            sheet_id = i['properties']['sheetId']
            # si l'id de la feuille est celle demandée
            if gid_gsheet == str(sheet_id) :
                # Obtenir les valeurs du Google Sheet
                result = sheet.values().get(spreadsheetId = id_gsheet, range = title).execute()
                values = result.get('values')
                return pd.DataFrame(columns = values[0], data = values[1:len(values)])
            # si l'id de la feuille n'est pas celle demandée
            else :
                pass
    except Exception as e:
        print(f"Erreur lors de l'import de Google Sheet : {e}")
        raise


@retry(
    stop = stop_after_attempt(5),
    wait = wait_exponential(multiplier = 2, min = 1, max = 20),
    retry = retry_if_exception_type(Exception)
)
def googleSheetExport(url, df):
    try:
        # Passer du dataframe au format adequat pour l'export sur googlesheet
        produit = df
        produit = produit.fillna('')
        Data = []
        Weight = produit.values.tolist()
        ColumnName = produit.keys().tolist()
        Data.append(ColumnName)
        for i in Weight :
            Data.append(i)

        # Format de l'url
        x = url

        id_gsheet = re.search('d\/([a-zA-Z0-9_-]+)', x).group(1)
        gid_gsheet = re.search('gid=([a-zA-Z0-9_-]+)', x).group(1)

        # Call Sheets API
        service = build('sheets', 'v4', credentials = creds)
        sheet = service.spreadsheets()
        sheet_metadata = service.spreadsheets().get(spreadsheetId = id_gsheet).execute()
        sheets = sheet_metadata.get('sheets', '')

        # boucle sur les pages du google sheet pour récupérer l'id de page
        for i in sheets :
            title = i['properties']['title']
            sheet_id = i['properties']['sheetId']
            if gid_gsheet == str(sheet_id) :
                NAME_PAGE = title

                # Supprimer les données présentes avant l'export
                clear = sheet.values().clear(spreadsheetId = id_gsheet, range = NAME_PAGE).execute()

                # Exporter les données dans le Google Sheet
                request = sheet.values().update(
                    spreadsheetId = id_gsheet,
                    range = NAME_PAGE,
                    valueInputOption = 'USER_ENTERED',
                    body = {'values' : Data}
                    ).execute()
            else :
                1
    except Exception as e:
        print(f"Erreur lors de l'export de Google Sheet : {e}")
        raise



@retry(
    stop = stop_after_attempt(5),
    wait = wait_exponential(multiplier = 2, min = 1, max = 20),
    retry = retry_if_exception_type(Exception)
)
def googleDocExportText(url, text):
    try:
        service = build('docs', 'v1', credentials = creds)

        # Extraire l'ID du document depuis l'URL
        doc_id = url.split('/d/')[1].split('/')[0]

        requests = [
            {
                'insertText': {
                    'location': {'index': 1},  # Position d'insertion (1 pour début du doc)
                    'text': text
                },
            }
        ]

        # Retrieve the documents contents from the Docs service.
        result = service.documents().batchUpdate(documentId = doc_id, body = {'requests': requests}).execute()

    except Exception as e:
        print(f"Erreur lors de l'export de Google Sheet : {e}")
        raise

@retry(
    stop = stop_after_attempt(5),
    wait = wait_exponential(multiplier = 2, min = 1, max = 20),
    retry = retry_if_exception_type(Exception)
)
def googleDocExportText_with_format(url, df_export):
    try:
        service = build('docs', 'v1', credentials = creds)

        # Extraire l'ID du document depuis l'URL
        doc_id = url.split('/d/')[1].split('/')[0]

        requests = []
        index = 1  # Position de départ dans le doc

        # Séparation du texte en paragraphes (chaque ligne devient un paragraphe)
        for i, row in df_export.iterrows():
            #print(index)
            keyword = row['Mot clef']
            print(keyword)

            # Ajout du texte
            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': "\n" + keyword.capitalize() + "\n" # Ajout de saut de ligne
                }
            })
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': index,
                        'endIndex': index + len(keyword)
                    },
                    'textStyle': {'bold': True, 'italic' : True, 'underline': False, 'foregroundColor': {'color': {'rgbColor': {'blue': 1.0,'green': 0.0,'red': 0.0}}}, 'fontSize' : {'magnitude' : 14, 'unit' : 'PT'}},
                    'fields': 'bold, italic, underline, foregroundColor, fontSize'
                }
            })

            index += len(keyword) + 2
            #print(index)

            paragraphs = row['Recommandations'].split("\n")
            for paragraph in paragraphs:
                #print(paragraph)
                # Ajout du texte
                requests.append({
                    'insertText': {
                        'location': {'index': index},
                        'text': paragraph + "\n"
                    }
                })

                # Mise en forme en gras si c'est un titre (ex : si ça finit par ":")
                if paragraph.strip().endswith(":"):
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': index,
                                'endIndex': index + len(paragraph)
                            },
                            'textStyle': {'bold': True, 'italic' : False, 'underline': True, 'foregroundColor': {'color': {'rgbColor': {'blue': 0.0,'green': 0.0,'red': 0.0}}}, 'fontSize' : {'magnitude' : 10, 'unit' : 'PT'}},
                            'fields': 'bold, italic, underline, foregroundColor, fontSize'
                        }
                    })
                elif len(paragraph) > 1:
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': index,
                                'endIndex': index + len(paragraph)
                            },
                            'textStyle': {'bold': False, 'italic' : False, 'underline': False, 'foregroundColor': {'color': {'rgbColor': {'blue': 0.0,'green': 0.0,'red': 0.0}}}, 'fontSize' : {'magnitude' : 10, 'unit' : 'PT'}},
                            'fields': 'bold, italic, underline, foregroundColor, fontSize'
                        }
                    })
                else:
                    pass

                index += len(paragraph) + 1  # Mise à jour de l'index pour éviter l'écrasement
                #print(index)

        # Exécution de la requête
        service.documents().batchUpdate(documentId = doc_id, body = {'requests': requests}).execute()

    except Exception as e:
        print(f"Erreur lors de l'export de Google Doc : {e}")
        raise
