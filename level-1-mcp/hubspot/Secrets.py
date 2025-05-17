


# !/usr/bin/env python3
"""
Setup script to initialize keyring with necessary credentials
Run this script once to set up all required credentials securely
"""

import keyring
import getpass
from keyring.backends import Windows
from config import Config

class Setup:
    def __init__(self):
        windows_backend = Windows.WinVaultKeyring()
        keyring.set_keyring(windows_backend)

    def setup_credentials(self):
        print("Setting up secure credentials for HubSpot integration")
        print("=" * 50)

        # Get service ID from config
        service_id = Config.hubspot["service_id"]

        # Get HubSpot access token
        print("\nHubSpot API Access Token")
        print("-" * 30)
        access_token = getpass.getpass("Enter your HubSpot access token: ")
        keyring.set_password(service_id, Config.hubspot["access_token_key"], access_token)

        print("\nCredentials stored successfully!")
        print("You can now run the main program.")


    def test_credentials(self):
        """Test if credentials are properly set in keyring"""
        service_id = Config.hubspot["service_id"]

        # Test HubSpot access token
        access_token = keyring.get_password(service_id, Config.hubspot["access_token_key"])
        if not access_token:
            return False, "HubSpot access token not found"

        return True, "All credentials found"


if __name__ == "__main__":
    setup = Setup()
    # Check if credentials already exist
    success, message = setup.test_credentials()

    if success:
        print("Credentials already exist in keyring.")
        choice = input("Do you want to reset credentials? (y/n): ").lower()
        if choice == 'y':
            setup.setup_credentials()
        else:
            print("Keeping existing credentials.")
    else:
        print(f"Missing credentials: {message}")
        setup.setup_credentials()