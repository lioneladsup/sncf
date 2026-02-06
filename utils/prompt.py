# Imports
import pandas as pd
import json
from utils import ggsheet, secrets
# pip install openai==0.28
import openai
import re
import random
import time
import statistics

########## Credentials ##########

def get_recommandation(text_prompt):
  openai.api_key = data_openai_api_key

  time.sleep(round(random.uniform(1, 10), 1))

  if len(text_prompt) < 16385:
    model = 'gpt-3.5-turbo'
  elif (len(text_prompt) >= 16385) & (len(text_prompt) < 32768):
    model = 'o1-preview-2024-09-12'
  elif (len(text_prompt) >= 32768) & (len(text_prompt) < 65536):
    model = 'o1-mini-2024-09-12'
  elif (len(text_prompt) >= 65536) & (len(text_prompt) < 100000):
    model = 'o1-mini-2024-09-12'
  else:
    model = 'o1-mini-2024-09-12'
    print('PROMPT TOO LARGE')

  print(f'Taille du prompt : {len(text_prompt)} - Model choisi : {model}')

  #print(text_prompt)

  try:
    completion = openai.ChatCompletion.create(
        model = model,
        messages = [{"role": "user", "content" : text_prompt}]
    )
    #print(completion['choices'][0]['message']['content'])
    #new_title = re.findall('"(.*)"', completion['choices'][0]['message']['content'])[0]
    #print(f'-> Nouveau titre : {new_title}\n')
    return completion['choices'][0]['message']['content'] # new_title
  except Exception as e:
    print(f"Erreur - {e}")
    return None


def process_recommandations(df_descriptions):
    df_descriptions['Nombre de mots'] = df_descriptions['Body'].fillna("").astype(str).apply(lambda x: len(x.split()))

    # Récupérer les prompts du SEO depuis ggsheet
    url_prompts = 'https://docs.google.com/spreadsheets/d/1hNJy2gA2epDAOgFAODd0RTrn0DDln2KkDR3tLa4IIDI/edit?gid=1205445978#gid=1205445978'
    df_prompt = ggsheet.googleSheetImport(url_prompts)
    df_prompt.head()

    # gestion des caractères spéciaux dans les searchs terms
    df_descriptions['Search_Term_clean'] = df_descriptions['Search Term'].apply(lambda x : x.replace('Ã©', 'é').replace('Ã\xa0', 'à'))

    list_motsclefs = df_descriptions['Search_Term_clean'].unique().tolist()

    # Créer élements de sortie
    list_sortie = []
    list_df_sortie = []

    # itérer sur les searchs terms
    for term in list_motsclefs:
        print(term)

        list_terms = []
        list_title = []
        list_metadescriptions = []
        list_importantfacts = []
        list_important_numbers = []
        list_terms.append(term)

        # requête gpt pour le titre
        text_prompt_title = df_prompt['proposition '].loc[df_prompt['Element'] == 'Title'].values[0].replace("{df['Search Term'].unique()}", term).replace("{df['Title'].unique().tolist()}", ' '.join(df_descriptions['Title'].loc[df_descriptions['Search_Term_clean'] == term].unique().tolist()))
        list_title.append(get_recommandation(text_prompt = text_prompt_title))

        # requête gpt pour la metadescription
        text_prompt_metadescription = df_prompt['proposition '].loc[df_prompt['Element'] == 'Meta description'].values[0].replace("{df['Search Term'].unique()}", term).replace("{df['Title'].unique().tolist()}", ' '.join(df_descriptions['Title'].loc[df_descriptions['Search_Term_clean'] == term].unique().tolist())).replace("{df['Meta Description'].unique().tolist()}", ' '.join(df_descriptions['Meta Description'].loc[df_descriptions['Search_Term_clean'] == term].unique().tolist()))
        list_metadescriptions.append(get_recommandation(text_prompt = text_prompt_metadescription))

        # requête gpt pour les importants facts
        text_prompt_importantfacts = df_prompt['proposition '].loc[df_prompt['Element'] == 'Important facts'].values[0].replace("{df['Search Term'].unique()}", term).replace("{df['Body'].unique().tolist()}", ' '.join(df_descriptions['Body'].loc[df_descriptions['Search_Term_clean'] == term].unique().tolist()))
        list_importantfacts.append(get_recommandation(text_prompt = text_prompt_importantfacts))

        # requête gpt pour les importants numbers
        text_prompt_importantnumbers = df_prompt['proposition '].loc[df_prompt['Element'] == 'Important numbers'].values[0].replace("{df['Search Term'].unique()}", term).replace("{df['Body'].unique().tolist()}", ' '.join(df_descriptions['Body'].loc[df_descriptions['Search_Term_clean'] == term].unique().tolist()))
        list_important_numbers.append(get_recommandation(text_prompt = text_prompt_importantnumbers))

        # Mise en forme des résultats (dataframe)
        print('dataframe')
        df_results = pd.DataFrame()
        df_results['Mot clé'] = list_terms
        df_results['Titres'] = list_title
        df_results['metadescriptions'] = list_metadescriptions
        df_results['Bigrams'] = ''.join([element for element in df_descriptions['Bigrams'].loc[df_descriptions['Search_Term_clean'] == term]]).replace('\n', ' ')
        df_results['Trigrams'] = ''.join([element for element in df_descriptions['Trigrams'].loc[df_descriptions['Search_Term_clean'] == term]]).replace('\n', ' ')
        df_results['TFIDF'] = ''.join([element for element in df_descriptions['TF-IDF Scores'].loc[df_descriptions['Search_Term_clean'] == term]]).replace('\n', ' ')
        df_results['Nb_mots_moyen'] = str(statistics.mean([float(element) for element in df_descriptions['Nombre de mots'].loc[df_descriptions['Search_Term_clean'] == term]]))
        df_results['importantfacts'] = list_importantfacts
        df_results['important_numbers'] = list_important_numbers
        list_df_sortie.append(df_results)

        # Préparation de la structure de sortir et ajout des trigram, etc
        print('structure sortie')
        '''
        structure_sortie_titre = 'Titre:\n' + df_results['Titres'][0]
        structure_sortie_metadescription = '\nMeta description:\n' + df_results['metadescriptions'][0]
        structure_sortie_nb = '\nBigram Frequency marquant :\n' + df_results['Bigrams'][0] + '\nTrigram Frequency marquant :\n' + df_results['Trigrams'][0] + '\nTF-IDF marquant :\n' + df_results['TFIDF'][0] + '\nLe nombre de mots moyen: :\n' + df_results['Nb_mots_moyen'][0]
        structure_sortie_importantfacts = '\nLes faits importants:\n' + df_results['importantfacts'][0]
        structure_sortie_important_numbers = '\nLes éléments chiffrés importants:\n' + df_results['important_numbers'][0]

        structure_sortie = structure_sortie_titre + '\n' + structure_sortie_metadescription + '\n' + structure_sortie_nb + '\n' + structure_sortie_importantfacts + '\n' + structure_sortie_important_numbers
        '''
        get_safe = lambda d, c: str(d.at[0, c]) if c in d.columns and pd.notna(d.at[0, c]) else ''

        structure_sortie_titre = 'Titre:\n' + get_safe(df_results, 'Titres')
        structure_sortie_metadescription = '\nMeta description:\n' + get_safe(df_results, 'metadescriptions')

        structure_sortie_nb = (
            '\nBigram Frequency marquant :\n' + get_safe(df_results, 'Bigrams') +
            '\nTrigram Frequency marquant :\n' + get_safe(df_results, 'Trigrams') +
            '\nTF-IDF marquant :\n' + get_safe(df_results, 'TFIDF') +
            '\nLe nombre de mots moyen: :\n' + get_safe(df_results, 'Nb_mots_moyen')
        )

        structure_sortie_importantfacts = '\nLes faits importants:\n' + get_safe(df_results, 'importantfacts')
        structure_sortie_important_numbers = '\nLes éléments chiffrés importants:\n' + get_safe(df_results, 'important_numbers')

        structure_sortie = (
            structure_sortie_titre +
            '\n' + structure_sortie_metadescription +
            '\n' + structure_sortie_nb +
            '\n' + structure_sortie_importantfacts +
            '\n' + structure_sortie_important_numbers
        )

        list_sortie.append(structure_sortie)

    # Export des résultats sur le ggsheet (onglet "resultats_prompt")
    df_export = pd.DataFrame()
    df_export['Mot clef'] = list_motsclefs
    df_export['Recommandations'] = list_sortie

    url_resultats_prompt = 'https://docs.google.com/spreadsheets/d/1hNJy2gA2epDAOgFAODd0RTrn0DDln2KkDR3tLa4IIDI/edit?gid=282244402#gid=282244402'
    print(df_export)
    #ggsheet.googleSheetExport(url_resultats_prompt, df_export)
    print(list_df_sortie)
    # Export des résultats sur le ggsheet (onglet "resultats_sortie")
    print('voici la liste')
    df_sortie_final = pd.concat(list_df_sortie)
    df_sortie_final.head()
    #df_sortie_final = df_sortie_final.drop(columns=['metadescriptions', 'Nb_mots_moyen'], inplace=True)
  
    url_sortie = 'https://docs.google.com/spreadsheets/d/1hNJy2gA2epDAOgFAODd0RTrn0DDln2KkDR3tLa4IIDI/edit?gid=32332676#gid=32332676'
    print('voici la sortie')
    print(df_sortie_final)
    ggsheet.googleSheetExport('https://docs.google.com/spreadsheets/d/1z73psp8YosM1KwwBd65jbFwXoq9Ki-zIPnI_eVkb7T0/edit?gid=1086639884#gid=1086639884', df_sortie_final)

    # Export des résultats sur un google doc
    url_google_doc = 'https://docs.google.com/document/d/1cpDtZhCl1Zt8E3Hw83LWXv0SHfXbX3bVIZsJbzuDJ1o/edit?tab=t.0'
    #ggsheet.googleDocExportText_with_format(url_google_doc, df_export)
    return df_sortie_final