########## Imports ##########
import pandas as pd
import json, re
import hmac
import hashlib
import datetime
from datetime import datetime
import pytz
import asyncio, nest_asyncio
nest_asyncio.apply()
import aiohttp
from tqdm import tqdm
from pandas import json_normalize
import tldextract
from urllib.parse import urlparse
#from utils import secrets, ggsheet
import serpapi
from serpapi import GoogleSearch



########## Credentials Authoritas ###########
#creds_authoritas_str = secrets.access_secret(secret_id = 'projects/318987655175/secrets/studi_salesforce_api')
#creds_authoritas = json.loads(creds_authoritas_str)

#creds_authoritas = json.load(open('../credentials/authoritas.json'))
creds_authoritas = json.load(open('credentials/authoritas.json'))

privateKey = creds_authoritas['privateKey']
publicKey = creds_authoritas['publicKey']
saltKey = creds_authoritas['saltKey']
url = creds_authoritas['url']


########## Fonctions Authoritas ##########

# Hash
presentDate = datetime.now()
unix_timestamp = datetime.timestamp(presentDate)
unix_timestamp_int = int(unix_timestamp)

message = str(unix_timestamp_int) + str(publicKey) + str(saltKey)
hmac_hash = hmac.new(privateKey.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

# Header
headers = {
    "Host": "instant.v3.api.authoritas.com",
    "Content-Type": "application/json",
    "Authorization": f"KeyAuth publicKey={publicKey} hash={hmac_hash} ts={unix_timestamp_int}"
}


# Fetch function
async def fetch(session, engine, query, sem, retry_limit = 10):
    data_object = {
        "search_engine": f"{engine}",
        "region": "fr",
        "language": "fr",
        "user_agent": "pc",
        "max_results": 50, # 10 -> 1 page, 20 -> 2 pages, etc
        #"phrase": ""
    }
    data_object['phrase'] = query
    json_object = json.dumps(data_object)
    attempt = 0
    for attempt in range(retry_limit):
        async with sem:
            try:
                async with session.post(url, headers = headers, data = json_object) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if not data.get('jid'):
                        print(f"Le champ 'jid' est False pour la requête \"{query}\". Relance de la requête...")
                    else:
                        return query, data
            except aiohttp.ClientError as e:
                pass
        attempt += 1
    return query, None

# Main function
async def main_authoritas(keywords, engine):
    sem = asyncio.Semaphore(25)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, engine, query, sem, retry_limit = 10) for query in keywords]

        results = []
        with tqdm(total = len(keywords)) as pbar:
            for coro in asyncio.as_completed(tasks):
                try:
                    query, data = await coro
                    if data:
                        #results.append((query, data))
                        results.append(data)
                        pass
                    pbar.update(1)
                except Exception as e:
                    print(f'Error occurred: {e}')
        return results

def virer_sites_relous(row):
    # ajouter un filtre pour virer tout ce qui est définition, conjugaison etc
    element_to_exclude = [
        'leparisien', 'wikipedia', 'larousse', 'wiktionary', 'info','cnrtl', 'conjugaison',
        'linternaute', 'lefigaro', 'lemonde', 'nouvelobs', 'reverso',
        'lerobert', 'bescherelle', 'wordreference', 'ouest-france', 'bfmtv', 'linguee'
    ]

    # Construire l'expression régulière à partir de la liste échappée
    pattern = r'(' + '|'.join(element_to_exclude) + ')'

    if re.search(pattern, str(row['url'])):
        #print(f"{str(row['url'])} -----> Oui")
        return 'Oui'
    else:
        #print(f"{str(row['url'])} -----> Non")
        return 'Non'
'''
def process_authoritas_data(keywords, search_engine):

    #results = await main_authoritas(keywords)
    list_results = []
    for engine in search_engine:
        print(engine)
        results = asyncio.run(main_authoritas(keywords, engine))
        i = 0
        for x in range(len(results)):
            for r in list(results[x]['response']['results']['organic'].keys()):
                globals()[f'df_results_{r}'] = json_normalize(results[x]['response']['results']['organic'][r])
                globals()[f'df_results_{r}']['Search term'] = keywords[i]
                globals()[f'df_results_{r}']['Search engine'] = engine
                list_results.append(globals()[f'df_results_{r}'])
            i += 1

    df_final = pd.concat(list_results)
    df_final['company'] = df_final['url'].apply(lambda x : tldextract.extract(x).domain)
    df_final['domain'] = df_final['url'].apply(lambda x : urlparse(x).netloc)

    df_final['drop'] = df_final.apply(virer_sites_relous, axis = 1)
    df_final_filtre = df_final.loc[df_final['drop'] == 'Non']
    df_final_filtre.drop(['drop'], axis = 1, inplace = True)

    # modifier l'ordre des colonnes
    df_final_filtre = df_final_filtre[['Search term', 'Search engine', 'page_number', 'markup', 'company', 'domain', 'title', 'url', 'description', 
        'visible', 'above_the_fold', 'top_left', 'bottom_right', 'header',
        'sub_type', 'steps.1',  'amp', 'carousel', 'rich_snippets', 'type'
        ]]

    df_final_filtre = df_final_filtre.fillna('')
    return df_final_filtre
'''

########## Fonctions SerpAPI ##########


def process_serpapi_data(keywords, search_engine):

    # Credentials
    #creds_serpapi = json.load(open('credentials/serpapi.json'))
    API_KEY = "b0a5e8b5810393fb8221594dfb210606c9ebc40d97589336cafdc1ad0ee98088"
    #API_KEY = creds_serpapi['API_KEY']

    # Get today date
    paris_tz = pytz.timezone('Europe/Paris')
    today_date = datetime.now(tz = paris_tz).strftime('%Y-%m-%d')

    list_df_results = []
    for engine in search_engine:
        print(engine)
        for term in keywords:

            # Set params
            params = {
            'engine': f'{engine}',
            'q': f'{term}', # query
            'location': 'France',
            'hl': 'fr', # langue
            'gl': 'fr',
            'google_domain': 'google.fr',
            'num': '5', # nombre de résultats à retourner
            'start': '0', # 1ère page
            'safe': 'active', # adult filter on
            'api_key': API_KEY
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results['organic_results']
            globals()[f'df_{term}'] = json_normalize(organic_results)
            globals()[f'df_{term}']['Search term'] = term
            globals()[f'df_{term}']['Search engine'] = engine
            list_df_results.append(globals()[f'df_{term}'])

    df_final = pd.concat(list_df_results)

    df_final.rename(columns = {'link' : 'url'}, inplace = True)
    df_final['company'] = df_final['url'].apply(lambda x : tldextract.extract(x).domain)
    df_final['domain'] = df_final['url'].apply(lambda x : urlparse(x).netloc)
    df_final['drop'] = df_final.apply(virer_sites_relous, axis = 1)
    df_final_filtre = df_final.loc[df_final['drop'] == 'Non']
    df_final_filtre.drop(['drop'], axis = 1, inplace = True)

    # modifier l'ordre des colonnes
    #df_final = df_final[['Search term', 'Search engine', 'position', 'company', 'domain', 'title', 'url', 'redirect_link', 'displayed_link',
        #'thumbnail', 'favicon', 'snippet', 'snippet_highlighted_words', 'source']]

    df_final = df_final.fillna('')

    return df_final









