import requests
import json
import datetime
import keyring
from hubspot.config import Config
from hubspot.postgres_client import PostgresClient


class HubSpotTool():
    """Class to interact with the HubSpot API"""

    def __init__(self, base_url=None):
        self.BASE_URL = base_url or Config.hubspot["base_url"]

        # Get configuration from config.py
        service_id = Config.hubspot["service_id"]
        access_token_key = Config.hubspot["access_token_key"]
        db_user_key = Config.hubspot["db_user_key"]
        db_password_key = Config.hubspot["db_password_key"]

        # Get HubSpot access token and database credentials from keyring
        self.hubspot_access_token = keyring.get_password(service_id, access_token_key)
        db_user = keyring.get_password(service_id, db_user_key)
        db_password = keyring.get_password(service_id, db_password_key)

        # Get database configuration from config file
        db_name = Config.database["name"]
        db_host = Config.database["host"]
        db_port = Config.database["port"]

        self.db_client = PostgresClient(
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            db_host=db_host,
            db_port=db_port
        )

    def __destruct__(self):
        # Close the database connection pool
        self.db_client.close()

    def call_hubspot_api_oauth(self, method, endpoint, data=None, params=None):
        """Helper function to make API calls using Bearer Token"""
        access_token = self.hubspot_access_token
        print("Calling ", endpoint, " method ", method, " with payload \n", data)

        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        print(f"Making {method} request to {url}")
        if params:
            print(f"Query parameters: {params}")
        if data:
            print(f"Request body: {json.dumps(data, indent=2)}")

        try:
            if method == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data, params=params)
            elif method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            print(f"Response Status Code: {response.status_code}")
            # Attempt to parse JSON response if content exists
            if response.content:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    print("Warning: Response was not JSON.")
                    return response.text  # Return plain text if not JSON
            else:
                print("Info: Response body is empty.")
                return None  # No content in response

        except requests.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response Body: {e.response.text}")
            return None

    def delete_lead(self, lead_id):
        """Delete a lead from HubSpot"""
        delete_lead_endpoint = f"/crm/v3/objects/contacts/{lead_id}"
        return self.call_hubspot_api_oauth(method='DELETE', endpoint=delete_lead_endpoint)

    def create_lead(self, lead_data: dict):

        # Example 1: Creating a new lead
        print("\n--- Creating a New Lead (Contact) using Private App Token ---")
        print(f"Lead data received: {json.dumps(lead_data, indent=2)}")
        """Create a new lead in HubSpot"""
        create_lead_endpoint = "/crm/v3/objects/contacts"
        created_lead_response = self.call_hubspot_api_oauth('POST', create_lead_endpoint, data=lead_data)

        if created_lead_response:
            print("Lead created successfully using Private App Token:")
            print(json.dumps(created_lead_response, indent=2))
            new_lead_id = created_lead_response.get('id')
            print(f"Newly created lead ID: {new_lead_id}")

            try:
                # Store the lead in PostgreSQL if created successfully
                db_id = self.db_client.store_lead(hubspot_id=new_lead_id, lead_data=lead_data)
            finally:
                return new_lead_id
        else:
            print("Failed to create lead using Private App Token.")
            return None

    def update_lead(self, properties: json):
        lead_id = properties.get('lead_id')
        """Update an existing lead in HubSpot"""
        modify_lead_endpoint = f"/crm/v3/objects/contacts/{lead_id}"
        return self.call_hubspot_api_oauth('PATCH', modify_lead_endpoint, data=properties)

    def create_meeting(self, meeting_data: dict):
        """Create a new meeting in HubSpot"""
        create_meeting_endpoint = "/crm/v3/objects/meetings"
        response = self.call_hubspot_api_oauth('POST', create_meeting_endpoint, data=meeting_data)
        meeting_id = response.get('meeting_id')
        lead_id = response.get('lead_id')
        if meeting_id:
            db_meeting_id = self.db_client.store_meeting(
                hubspot_id=meeting_id,
                lead_id=lead_id,
                title=meeting_data["properties"]["hs_meeting_title"],
                start_time=meeting_data["properties"]["start_time"],
                end_time=meeting_data["properties"]["end_time"]
            )

        return response


hstool = HubSpotTool()


def create_lead(json_payload: dict):
    print('Agent called "create_lead()"')
    return hstool.create_lead(json_payload)
