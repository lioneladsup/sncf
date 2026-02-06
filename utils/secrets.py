########## IMPORTS ##########
import pandas as pd
import json, os

# Secret Manager
from google.cloud import secretmanager

# Varialble that will indicate if we run the script on our machine or github server
LOCAL = os.getenv('LOCAL')

########## FONCTIONS ##########

def access_secret(secret_id, version_id = 'latest'):
    """ Return the value of a secret's latest version"""
    from google.cloud import secretmanager
    # Create the secret manager client
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version
    name = f"{secret_id}/versions/{version_id}"

    # Access the secret version
    response = client.access_secret_version(name = name)

    # Return the decoded payload
    return response.payload.data.decode('UTF-8') # -> problème -> retourne un st





########## END ##########