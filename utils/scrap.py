from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

stop_words = set(stopwords.words("french"))

# Fonctions utilitaires
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower()

def remove_stopwords(tokens):
    return [word for word in tokens if word not in stop_words]

def get_ngrams(text, n):
    tokens = clean_text(text).split()
    filtered_tokens = remove_stopwords(tokens)
    return list(ngrams(filtered_tokens, n))

def analyze_text(text):
    tokens = clean_text(text).split()
    filtered_tokens = remove_stopwords(tokens)
    keyword_counts = Counter(filtered_tokens)
    bigrams = Counter(get_ngrams(text, 2))
    trigrams = Counter(get_ngrams(text, 3))
    return keyword_counts, bigrams, trigrams

def calculate_tfidf(documents):
    vectorizer = TfidfVectorizer(stop_words=list(stop_words), max_features=30)
    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1
    tfidf_scores = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
    return tfidf_scores

def extract_tables(driver):
    tables = driver.find_elements(By.TAG_NAME, "table")
    table_data = []
    for table in tables:
        rows = table.find_elements(By.TAG_NAME, "tr")
        table_content = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td") or row.find_elements(By.TAG_NAME, "th")
            table_content.append([cell.text for cell in cells])
        table_data.append(table_content)
    return table_data

def extract_sources(driver):
    links = driver.find_elements(By.TAG_NAME, "a")
    sources = [link.get_attribute("href") for link in links if link.get_attribute("href")]
    return sources

def extract_important_elements(driver):
    lists = driver.find_elements(By.TAG_NAME, "ul")
    list_items = []
    for ul in lists:
        items = ul.find_elements(By.TAG_NAME, "li")
        list_items.extend([item.text for item in items])
    return list_items

def extract_tables(soup):
    """Extrait les données des tables HTML."""
    tables = soup.find_all("table")
    table_data = []
    for table in tables:
        rows = table.find_all("tr")
        table_content = [[cell.get_text(strip=True) for cell in row.find_all(["td", "th"])] for row in rows]
        table_data.append(table_content)
    return table_data

def extract_sources(soup):
    """Extrait les liens présents dans la page."""
    links = soup.find_all("a", href=True)
    sources = [link["href"] for link in links]
    return sources

def extract_important_elements(soup):
    """Extrait les éléments importants comme les listes."""
    lists = soup.find_all("ul")
    list_items = [item.get_text(strip=True) for ul in lists for item in ul.find_all("li")]
    return list_items

def analyze_page_from_response(url):
    # Création de l'objet BeautifulSoup
    payload = { 'api_key': 'ebf4b9050aa365e505f8a0d4618a885a', 'url': url }
    r = requests.get('https://api.scraperapi.com/', params=payload)
    soup = BeautifulSoup(r.content, "html.parser")

    # 1. Titre de la page
    title = soup.title.string if soup.title else "Titre non trouvé"

    # 2. Méta-description
    meta_description_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_description_tag["content"] if meta_description_tag else "Méta-description non trouvée"

    # 3. Texte principal (body)
    body = soup.get_text(separator=' ', strip=True)
    #body = str(soup.body)
    #print(body)

    # 4. Extraction des titres (h1 à h6)
    headings = [h.get_text(strip=True) for h in soup.find_all(re.compile("^h[1-6]$"))]

    # 5. Analyse de texte pour les mots-clés, bigrammes et trigrammes
    keyword_counts, bigrams, trigrams = analyze_text(body)

    # 6. TF-IDF sur le contenu du body
    tfidf_scores = calculate_tfidf([body])

    # 7. Extraction des tables
    tables = extract_tables(soup)

    # 8. Extraction des sources (liens)
    sources = extract_sources(soup)

    # 9. Extraction des éléments importants (listes)
    #important_elements = extract_important_elements(soup)

    # Compilation des résultats
    page_analysis = {
        "title": title,
        "meta_description": meta_description,
        "body": body[:],  # Premier extrait du body
        "headings": headings,
        "keywords": keyword_counts.most_common(10),
        "bigrams": bigrams.most_common(10),
        "trigrams": trigrams.most_common(10),
        "tfidf_scores": tfidf_scores[:30],
        "tables": tables,
        "sources": sources,
    }

    return page_analysis


def clean_list(elements, limit=None):
    """
    Nettoie une liste en supprimant les éléments vides ou None et retourne une chaîne formatée.
    Si un `limit` est fourni, ne garde que les `limit` premiers éléments.
    """
    cleaned_elements = [el for el in elements if el.strip()]  # Supprimer les éléments vides
    if limit:
        cleaned_elements = cleaned_elements[:limit]
    return "\n".join(cleaned_elements)


def analyze_multiple_pages(urls, companies, search_terms):
    """
    Analyse une liste d'URLs et retourne un DataFrame avec une ligne par URL, incluant des colonnes supplémentaires.
    
    Args:
    - urls (list): Liste des URLs à analyser.
    - companies (list, optional): Liste des noms de sociétés associées à chaque URL.
    - search_terms (list, optional): Liste des termes de recherche associés à chaque URL.
    
    Returns:
    - pd.DataFrame: DataFrame contenant les résultats de l'analyse.
    """
    results = []

    for i, url in enumerate(urls):
        print(f"Analyse de l'URL : {url}")
        try:
            analysis = analyze_page_from_response(url)
            
            result = {
                "URL": url,
                "Title": analysis.get("title", "").strip(),
                "Meta Description": analysis.get("meta_description", "").strip(),
                "Body": analysis.get("body", "").strip()[:],
                "Headings": clean_list(analysis.get("headings", [])),
                "Keywords": clean_list([f"{k} ({v})" for k, v in analysis.get("keywords", [])]),
                "Bigrams": clean_list([f"{' '.join(b)} ({v})" for b, v in analysis.get("bigrams", [])]),
                "Trigrams": clean_list([f"{' '.join(t)} ({v})" for t, v in analysis.get("trigrams", [])]),
                "TF-IDF Scores": clean_list([f"{word} ({score:.2f})" for word, score in analysis.get("tfidf_scores", [])]),
                "Sources": clean_list(analysis.get("sources", []), limit=10),
            }

            # Ajouter Company et Search Term si disponibles
            if companies:
                result["Company"] = companies[i] if i < len(companies) else ""
            if search_terms:
                result["Search Term"] = search_terms[i] if i < len(search_terms) else ""

            results.append(result)

        except Exception as e:
            print(f"Erreur lors de l'analyse de {url}: {e}")
            results.append({
                "URL": url,
                "Title": "",
                "Meta Description": "",
                "Body": "",
                "Headings": "",
                "Keywords": "",
                "Bigrams": "",
                "Trigrams": "",
                "TF-IDF Scores": "",
                "Sources": "",
                "Error": str(e),
                #"Company": companies[i] if companies and i < len(companies) else "",
                #"Search Term": search_terms[i] if search_terms and i < len(search_terms) else ""
                "Company": companies.iloc[i] if isinstance(companies, pd.Series) and not companies.empty and i < len(companies) else "",
                "Search Term": search_terms.iloc[i] if isinstance(search_terms, pd.Series) and not search_terms.empty and i < len(search_terms) else ""

            })

    # Convertir les résultats en DataFrame
    df = pd.DataFrame(results)

    # Réorganiser les colonnes pour que 'Company' et 'Search Term' soient en première position
    cols = ['Company', 'Search Term'] + [col for col in df.columns if col not in ['Company', 'Search Term']]
    df = df[cols]
    
    return df
