########## Imports ##########
import json, os
import pandas_gbq
from utils import secrets
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, time
from oauth2client.client import GoogleCredentials
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

########## Credentials ##########

# Varialble that will indicate if we run the script on our machine or github server
LOCAL = os.getenv('LOCAL')

service_account_bigquery_str = secrets.access_secret(secret_id = 'projects/318987655175/secrets/bigquery')
service_account_bigquery = json.loads(service_account_bigquery_str)

BQ_PROJECT_ID = 'adsupdata'
#BQ_DATASET_ID = 'omnes_data'

########## FONCTIONS ##########
@retry(
    stop = stop_after_attempt(5),
    wait = wait_exponential(multiplier = 2, min = 1, max = 20),
    retry = retry_if_exception_type(Exception)
)
def import_data(BQ_DATASET_ID, table):
    try:
        table_name =  table.replace(' ', '')
        bq_dataset = BQ_DATASET_ID
        bq_creds = service_account.Credentials.from_service_account_info(service_account_bigquery)
        client = bigquery.Client(project = BQ_PROJECT_ID, credentials = bq_creds)
        table_id = f'{BQ_PROJECT_ID}.{bq_dataset}.{table_name}'
        query = f"SELECT * FROM {table_id}"
        query_job = client.query(query)
        df = query_job.result().to_dataframe()
        return df
    except Exception as e:
        print("Erreur lors de l'import des données depuis Big query :", str(e))

@retry(
    stop = stop_after_attempt(5),
    wait = wait_exponential(multiplier = 2, min = 1, max = 20),
    retry = retry_if_exception_type(Exception)
)
def export_data_to_bq(BQ_DATASET_ID, data, table):
    try:
        table_name =  table.replace(' ', '')
        table_id = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{table_name}"
        bq_creds = service_account.Credentials.from_service_account_info(service_account_bigquery)
        pandas_gbq.to_gbq(
            data,
            table_id,
            project_id = BQ_PROJECT_ID,
            if_exists = 'replace',
            credentials = bq_creds,
            progress_bar = False
            )
        print('* ->  succès')

    except Exception as e:
        print("Erreur lors de l'export vers Big query :", str(e))

########## END ##########