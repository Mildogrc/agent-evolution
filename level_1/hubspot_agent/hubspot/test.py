import requests
import json
# import datetime
import keyring

# Local imports
from .config import Config
from .postgres_client import PostgresClient
from .hubspot_templates import new_lead_template

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
        if not self.hubspot_access_token:
            print("ERROR: HubSpot access token not found in keyring.")
        
        self.db_client = PostgresClient(
            db_name=Config.database["name"],
            db_user=keyring.get_password(service_id, db_user_key),
            db_password=keyring.get_password(service_id, db_password_key),
            db_host=Config.database["host"],
            db_port=Config.database["port"]
        )
        print("HubSpotTool initialized. DB Client configured.")

    def __del__(self):
        if hasattr(self, 'db_client') and self.db_client:
            self.db_client.close()
            print("PostgresClient connection pool closed.")

    def call_hubspot_api_oauth(self, method, endpoint, data=None, params=None):
        if not self.hubspot_access_token:
            # ... (error handling as before)
            error_message = "HubSpot API call failed: Access token is missing."
            print(f"ERROR: {error_message}")
            return {"status": "error", "message": error_message, "category": "authentication_error"}


        access_token = self.hubspot_access_token
        print(f"Calling {endpoint} method {method} with input data (from LLM/tool method):\n{json.dumps(data, indent=2) if data else 'No input data'}")
        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
        print(f"Making {method} request to {url}")

        request_body_for_hubspot = data
        if data and (method == 'POST' or method == 'PATCH'):
            try:
                # new_lead_template expects a flat dict of properties and wraps it in {"properties": ...}
                formatted_data = self.new_lead_template(data)
                print(f"Formatted request body by new_lead_template for HubSpot API: {json.dumps(formatted_data, indent=2)}")
                request_body_for_hubspot = formatted_data
            except KeyError as ke:
                error_message = f"Error during new_lead_template formatting: Missing key {ke} in LLM payload. LLM payload was: {data}"
                print(f"ERROR: {error_message}")
                return {"status": "error", "message": error_message, "category": "llm_payload_formatting_error"}
            except Exception as e:
                error_message = f"Generic error during new_lead_template formatting: {e}. Original data: {data}"
                print(f"ERROR: {error_message}")
                return {"status": "error", "message": error_message, "category": "template_formatting_error"}
        
        try:
            response_action = getattr(requests, method.lower(), None)
            if not response_action:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if method in ['POST', 'PATCH']:
                response = response_action(url, headers=headers, json=request_body_for_hubspot, params=params)
            else: # GET, DELETE
                response = response_action(url, headers=headers, params=params)

            print(f"Raw Response Status Code: {response.status_code}")
            response.raise_for_status()
            
            if response.content:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"status": "success_but_not_json", "content": response.text}
            else:
                return {"status": "success", "message": f"{method} request to {endpoint} successful with no content."}

        except requests.exceptions.HTTPError as http_err:
            response_text = http_err.response.text if hasattr(http_err.response, 'text') else str(http_err)
            error_message = f"HubSpot API HTTP error: {http_err.response.status_code} - {response_text}"
            print(f"ERROR: {error_message}")
            try:
                hubspot_error_details = http_err.response.json()
                # Add status code to the details from HubSpot if not present
                if 'status_code' not in hubspot_error_details:
                    hubspot_error_details['http_status_code'] = http_err.response.status_code
                return {"status": "error", "message": f"HubSpot API Error: {hubspot_error_details.get('message', response_text)}", "hubspot_error_details": hubspot_error_details}
            except json.JSONDecodeError:
                return {"status": "error", "message": error_message, "details": response_text}
        except requests.exceptions.RequestException as e:
            error_message = f"Network or request error: {e}"
            print(f"ERROR: {error_message}")
            return {"status": "error", "message": error_message, "category": "network_error"}

    def create_lead(self, json_payload_from_llm: dict):
        print("\n--- HubSpotTool METHOD: Creating a New Lead (Contact) ---")
        print(f"Payload received by HubSpotTool.create_lead (from LLM): {json.dumps(json_payload_from_llm, indent=2)}")

        # Validate that json_payload_from_llm is a flat dictionary of properties
        if not isinstance(json_payload_from_llm, dict) or "properties" in json_payload_from_llm:
            error_msg = "Tool Error: json_payload_from_llm for create_lead should be a flat dictionary of properties, not nested."
            print(f"ERROR: {error_msg} Payload was: {json_payload_from_llm}")
            return json.dumps({"status": "error", "message": error_msg, "category": "llm_payload_structure_error"})

        create_lead_endpoint = "/crm/v3/objects/contacts"
        created_lead_response = self.call_hubspot_api_oauth('POST', create_lead_endpoint, data=json_payload_from_llm)

        if created_lead_response and isinstance(created_lead_response, dict):
            if created_lead_response.get('status') == 'error': # Error from call_hubspot_api_oauth or HubSpot
                print(f"ERROR: HubSpot API call failed during create_lead: {created_lead_response.get('message')}")
                # Forward the detailed error from HubSpot if available
                return json.dumps(created_lead_response)

            if created_lead_response.get('id'): # HubSpot success
                new_lead_id = created_lead_response.get('id')
                print(f"HubSpot API: Lead created successfully. ID: {new_lead_id}")

                # For DB storage, use the flat dictionary of properties from the LLM.
                properties_for_db = json_payload_from_llm

                try:
                    db_id = self.db_client.store_lead(hubspot_id=new_lead_id, lead_data=properties_for_db)
                    print(f"DB: Lead {new_lead_id} stored successfully with DB ID {db_id}.")
                    return json.dumps({"status": "success", "message": f"Lead created successfully in HubSpot (ID: {new_lead_id}) and stored in DB (ID: {db_id}).", "hubspot_id": new_lead_id, "db_id": db_id})
                except Exception as e:
                    db_error_msg = f"Error storing lead {new_lead_id} in DB: {e}"
                    print(f"ERROR: {db_error_msg}")
                    ret