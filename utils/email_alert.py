########## Imports ##########
import json
import logging
from datetime import datetime

from utils import secrets

# Email
# https://support.google.com/accounts/answer/185833?hl=fr&sjid=17674000742249663040-EU

import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Warnings
import sys
import warnings
if not sys.warnoptions:
    warnings.simplefilter('ignore')

# Login infos
email_logins_info_str = secrets.access_secret(secret_id = 'projects/318987655175/secrets/gmail_send_email_data')
email_logins_info = json.loads(email_logins_info_str)

EMAIL_ADDRESS = email_logins_info['smtp_username']
EMAIL_PASSWORD = email_logins_info['smtp_password']

def log_error(exception, school_name, additional_info = None):
    """
    Enregistre une erreur dans un fichier log

    :param exception: L'exception levée
    :param school_name: Nom ou identifiant de l'école concernée
    :param additional_info: Autres informations utiles (facultatif)
    """
    # Configuration du logging si non déjà configuré
    logging.basicConfig(
        filename = 'error_log.txt', # Fichier où les erreurs seront stockées
        level = logging.ERROR, # Niveau de sévérité : ERROR
        format = '%(asctime)s - %(levelname)s - %(message)s' # Format des logs
    )

    # Message à enregistrer
    error_message = f"Erreur pour l'école {school_name}: {str(exception)}"
    if additional_info:
        error_message += f" | Infos supplémentaires: {additional_info}"

    # Log de l'erreur
    logging.error(error_message)


def email(subject, body, receiver_email, file = None):
    """
    Fonction pour envoyer un mail
    -----------------------------

    subject : sujet/objet du mail
    body : corps/contenu du mail
    receiver_email : adresse mail du destinataire
    file : pièce jointe (facultative)

    """

    # Création du message multipart et ajout des headers
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = EMAIL_ADDRESS
    message['To'] = receiver_email

    # Ajout du corps du mail
    message.attach(MIMEText(body, 'plain'))

    # Gestion de la pièce jointe si fournie
    if file:
        try:
            with open(file, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename = {file}')
            message.attach(part)
        except FileNotFoundError:
            print(f"Le fichier {file} est introuvable.")
            return

    # Conversion du message en chaîne de texte
    text = message.as_string()

    # Connexion au serveur SMTP et envoi de l'email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, receiver_email, text)
        print("Email envoyé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")