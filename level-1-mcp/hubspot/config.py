

class Config:
    def __init__(self):
        pass

    # Database configuration
    database = {
        "name": "slsfrcagent",  # Database name
        "host": "localhost",  # Database host
        "port": 5432  # Database port
    }

    # HubSpot configuration
    hubspot = {
        "base_url": "https://api.hubspot.com",
        "service_id": "hubspot_service",  # Service ID for keyring
        "access_token_key": "access_token",  # Key name for access token in keyring
        "db_user_key": "db_user",  # Key name for database username in keyring
        "db_password_key": "db_password"  # Key name for database password in keyring
    }