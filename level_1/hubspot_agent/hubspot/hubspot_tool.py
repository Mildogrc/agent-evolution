import requests
import json
import datetime
import keyring

# Local imports
from .config import Config
from .postgres_client import PostgresClient

from google.adk.tools import FunctionTool


class HubSpotTool():
    """Class to interact with the HubSpot API"""

    def __init__(self, base_url=None):
        self.BASE_URL = base_url or Config.hubspot["base_url"]

        service_id = Config.hubspot["service_id"]
        access_token_key = Config.hubspot["access_token_key"]
        db_user_key = Config.database["db_user_key"]
        db_password_key = Config.database["db_password_key"]

        self.hubspot_access_token = keyring.get_password(service_id, access_token_key)
        db_user = keyring.get_password(service_id, db_user_key)
        db_password = keyring.get_password(service_id, db_password_key)

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

    def __del__(self):
        if hasattr(self, 'db_client') and self.db_client:
            self.db_client.close()
            print("PostgresClient connection pool closed.")

    @staticmethod
    def new_lead_template(lead_data:dict):
        return {
            "properties": {
                "email": lead_data["email"],
                "firstname": lead_data["firstname"],
                "lastname": lead_data["lastname"],
                "phone": lead_data["phone"],
                "company": lead_data["company"],
                "website": lead_data["website"],
                "lifecyclestage": "lead"
            }
        }

    @staticmethod
    def update_lead_template(phone=None, state=None, lead_status=None):
        properties = {"properties": {}}

        if phone:
            properties["properties"]["phone"] = phone
        if state:
            properties["properties"]["state"] = state
        if lead_status:
            properties["properties"]["hs_lead_status"] = lead_status

        return properties

    @staticmethod
    def meeting_template(start_time, end_time, lead_id, title, body):
        return {
            "properties": {
                "hs_timestamp": start_time,
                "hs_meeting_body": body,
                "hs_meeting_end_time": end_time,
                "hs_meeting_title": title,
            },
            "associations": [
                {
                    "to": {
                        "id": lead_id
                    },
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 191  # Contact to Meeting association type ID
                        }
                    ]
                }
            ],
            "private": False
        }

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
        
        # Use the imported new_lead_template if data is present for POST/PATCH
        # This assumes new_lead_template formats the data specifically for HubSpot API
        request_body_data = data
        if data and (method == 'POST' or method == 'PATCH'):
            # Assuming new_lead_template takes the raw lead_data and formats it
            # into the structure HubSpot expects (e.g., with a "properties" key)
            formatted_data = self.new_lead_template(data) 
            print(f"Formatted request body: {json.dumps(formatted_data, indent=2)}")
            request_body_data = formatted_data # Use the formatted data for the request
        elif data:
             print(f"Request body (raw): {json.dumps(data, indent=2)}")


        try:
            if method == 'POST':
                response = requests.post(url, headers=headers, json=request_body_data, params=params)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=request_body_data, params=params)
            elif method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            print(f"Response Status Code: {response.status_code}")
            
            if response.content:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    print("Warning: Response was not JSON.")
                    return response.text
            else:
                print("Info: Response body is empty.")
                return None

        except requests.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response Body: {e.response.text}")
            return None

    def create_lead(self, lead_data: dict):
        print("\n--- Creating a New Lead (Contact) ---")
        create_lead_endpoint = "/crm/v3/objects/contacts"
        created_lead_response = self.call_hubspot_api_oauth('POST', create_lead_endpoint, data=lead_data)

        if created_lead_response and isinstance(created_lead_response, dict) and created_lead_response.get('id'):
            print("Lead created successfully:")
            new_lead_id = created_lead_response.get('id')
            print(f"Newly created lead ID: {new_lead_id}")

            try:
                db_id = self.db_client.store_lead(hubspot_id=new_lead_id, lead_data=lead_data)
            except Exception as e:
                print(f"Error storing lead in DB: {e}")
            return new_lead_id
        else:
            print(f"Failed to create lead. Response: {created_lead_response}")
            return None

    def update_lead(self, properties: dict):
        lead_id = properties.get('lead_id')
        if not lead_id:
            print("Error: lead_id missing from properties for update_lead.")
            return {"status": "error", "message": "lead_id is required for updating a lead."}
            
        modify_lead_endpoint = f"/crm/v3/objects/contacts/{lead_id}"
        
        # HubSpot expects the properties to be updated under a "properties" key in the payload
        payload_for_update = {"properties": properties}

        response = self.call_hubspot_api_oauth('PATCH', modify_lead_endpoint, data=payload_for_update) 
        return response

    def create_meeting(self, meeting_data: dict): 
        create_meeting_endpoint = "/crm/v3/objects/meetings"
        
        # Assuming meeting_data is already in the correct format for HubSpot API
        response = self.call_hubspot_api_oauth('POST', create_meeting_endpoint, data=meeting_data)
        
        meeting_id = None
        lead_id = None 
        
        if response and isinstance(response, dict):
            meeting_id = response.get('id') 
            if "associations" in meeting_data:
                for assoc in meeting_data.get("associations", []):
                    # Assuming HubSpot contact object type ID is "0-1"
                    if assoc.get("to", {}).get("objectTypeId") == "0-1" and assoc.get("to", {}).get("id"):
                        lead_id = assoc.get("to", {}).get("id")
                        break
        
        if meeting_id: 
            try:
                db_meeting_id = self.db_client.store_meeting(
                    hubspot_id=meeting_id,
                    lead_id=lead_id, 
                    title=meeting_data.get("properties", {}).get("hs_meeting_title"),
                    start_time=meeting_data.get("properties", {}).get("hs_timestamp"), 
                    end_time=meeting_data.get("properties", {}).get("hs_meeting_end_time")
                )
            except Exception as e:
                print(f"Error storing meeting in DB: {e}")
        return response

hstool = HubSpotTool()

def create_lead(json_payload:dict):    
    """Create a new lead (contact) in HubSpot and store it in the local database.

    This function creates a new contact in HubSpot using the HubSpot API and then stores
    the lead information in a local PostgreSQL database for tracking purposes.

    Args:
        json_payload (dict): A dictionary containing the lead's properties. This dictionary
            is passed directly to the HubSpot API, so it should be structured
            with a top-level "properties" key, which itself is a dictionary of HubSpot contact properties.
            Example:
            {
                "properties": {
                    "email": "contact@example.com",
                    "firstname": "John",
                    "lastname": "Doe",
                    "phone": "123-456-7890",
                    "company": "Example Corp",
                    "website": "https://example.com",
                    "lifecyclestage": "lead"
                }
            }
    Returns:
        str: The HubSpot ID of the newly created lead if successful, None if the creation fails.
    """
    print('Agent called "create_lead()"')
    return hstool.create_lead(json_payload)

create_lead_tool = FunctionTool(func=create_lead)