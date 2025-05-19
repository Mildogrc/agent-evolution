import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
            pass
   
    load_dotenv(dotenv_path='.env')
   
    gcp_project = os.getenv("GOOGLE_PROJECT")
    db_name = os.getenv("POSTGRES_DB")

    # Database configuration
    database = {
        "name": db_name,  # Database name
        "host": "localhost",  # Database host
        "port": 5432,  # Database port
        "db_user_key": "db_user",  # Key name for database username in keyring
        "db_password_key": "db_password"  # Key name for database password in keyring
    }

    # HubSpot configuration
    hubspot = {
        "base_url": "https://api.hubspot.com",
        "service_id": "hubspot_service",  # Service ID for keyring
        "access_token_key": "access_token",  # Key name for access token in keyring
    }

    # Email configuration
    email = {
        "imap_server": "your_imap_server.com",
        "email_address": "your_email@example.com"
    }

    # Google Cloud configuration
    gcp = {
        "gcp_project": gcp_project
    }