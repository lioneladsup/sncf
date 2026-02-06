########## IMPORTS ##########
import yaml, json
import pandas as pd
from utils import bigquery_data, email_alert, fonctions, ggsheet, scrap, prompt
from IPython.display import display

# Dates
from datetime import date, datetime, timedelta, time

########## CODE ##########

def main():
    #try:
    with open('Clients/clients_config.yml') as f:
        clients = yaml.safe_load(f)

        for client in clients['clients']:
            if client['compilation'] == True:
                print('> Start processing of the client: [', client['name'], ']')

                with open(f'Clients/{client["name"]}/report_definition.json') as f:
                    df_client = ggsheet.googleSheetImport('https://docs.google.com/spreadsheets/d/1KrH32tas-FamWZikQQLVm9jDSKg88OWUnY0s3bx-FLQ/edit?gid=269517263#gid=269517263')
                    df_client = df_client[df_client['jour de publication'] == '3'].reset_index(drop=True)
                    #df_client = df_client.iloc[41:105]

                    print(df_client)
                    report_definition = json.load(f)
                    keywords = df_client['keywords'].tolist()
                    url_client = df_client['URL'].tolist()
                    name_client = df_client['client'].tolist()

                    '''
                    keywords = report_definition['keywords']
                    url_client = report_definition['urls']
                    name_client = report_definition['client']
                    '''

                    search_engine = report_definition['search_engine']
                    scraping_method = report_definition['scraping_method']

                    if 'authoritas' in scraping_method:
                        print('     * getting concurrents list from Authoritas API')
                        df_authoritas = fonctions.process_authoritas_data(keywords, search_engine)
                        #display(df_authoritas.head())
                        df_authoritas_export = df_authoritas.astype(str)
                        ggsheet.googleSheetExport(client['url_export_authoritas'], df_authoritas_export)

                    if 'serpapi' in scraping_method:
                        print('     * getting concurrents list from SerpAPI')
                        df_serpapi = fonctions.process_serpapi_data(keywords, search_engine)
                        #display(df_serpapi.sample(10))
                        df_serpapi_export = df_serpapi.astype(str)
                        ggsheet.googleSheetExport(client['url_export_serpapi'], df_serpapi_export)
                        # Exemple d'utilisation
                        urls_to_analyze = df_serpapi_export['url'].tolist()
                        companies = df_serpapi_export['company'].tolist()
                        search_terms = df_serpapi_export['Search term'].tolist()
                        df_scrap = scrap.analyze_multiple_pages(urls_to_analyze,companies, search_terms)
                        df_scrap_client = scrap.analyze_multiple_pages(url_client, name_client, keywords)
                        df_scrap_client = df_scrap_client[['Search Term', 'Body', 'Headings']]
                        print('start_body')

                        print(df_scrap_client)

                        #ggsheet.googleSheetExport(client['url_scrap'], df_scrap)
                        #df_scrap.to_csv("export_scrap.csv", index=False, encoding="utf-8")
                        print('start_prompt')
                        df_concurrents = prompt.process_recommandations(df_scrap)
                        #print(df_concurrents)


                        df_final = pd.merge(df_concurrents, df_scrap_client, left_on='Mot clé', right_on='Search Term', how='left')
                        #print(df_final)
                        df_final.drop(columns=['metadescriptions', 'Nb_mots_moyen'], inplace=True)

                        #ggsheet.googleSheetExport(client['url_final'], df_flinal)
                        df_final.to_csv("sncf7.csv", index=False, encoding="utf-8")



    #except Exception as e:
        #print(e)
        #titre = f'Erreur code - optimizepage'
        #body += '\n' + str(e) + '\n'
        #email_alert.email(titre, body, 'lucile@ads-up.fr')


if __name__ == '__main__':
    main()

########## END ##########