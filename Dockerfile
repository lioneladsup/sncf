# Utiliser une image de base Python
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt /app/
COPY download_nltk_resources.py /app/

# Installer les dépendances
RUN python -m pip install --no-cache-dir -r requirements.txt

# Télécharger les ressources NLTK
RUN python /app/download_nltk_resources.py

# Copier le reste des fichiers après les étapes critiques
COPY . /app/

# Exposer le port 8501 (port par défaut pour Streamlit)
EXPOSE 8080

# Commande pour démarrer l'application Streamlit
CMD ["streamlit", "run", "app_optimize.py", "--server.port", "8080", "--server.enableCORS", "false"]
