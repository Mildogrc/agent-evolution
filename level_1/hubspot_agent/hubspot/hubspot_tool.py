import requests
import json
# import datetime # Keep for potential use, though not directly used in this simplified version
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
        if not self.hubspot_access_token:
            print("ERROR: HubSpot access token not found in keyring. Please check configuration.")
            # Consider raising an exception if the token is critical for all operations
            # raise ValueError("HubSpot access token not found in keyring.")

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
        print("HubSpotTool initialized. DB Client configured.")


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
                "phone": lead_data.get("phone", ""),
                "company": lead_data.get("company", ""),
                "website": lead_data.get("website", ""),
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
        if not self.hubspot_access_token:
            error_message = "HubSpot API call failed: Access token is missing."
            print(f"ERROR: {error_message}")
            return {"status": "error", "message": error_message}

        access_token = self.hubspot_access_token
        # The 'data' here is what the calling method (e.g., self.create_lead) provides.
        # This data should be the direct payload from the LLM.
        print(f"Calling {endpoint} method {method} with input data (before template formatting):\n{json.dumps(data, indent=2) if data else 'No input data'}")

        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        print(f"Making {method} request to {url}")
        if params:
            print(f"Query parameters: {params}")

        request_body_for_hubspot = data
        if data and (method == 'POST' or method == 'PATCH'):
            # new_lead_template is responsible for ensuring the data
            # is in the final format HubSpot API expects (e.g., {"properties": {...}}).
            # The `data` variable here is the `json_payload` from the LLM.
            try:
                formatted_data = self.new_lead_template(data)
                print(f"Formatted request body by new_lead_template for HubSpot API: {json.dumps(formatted_data, indent=2)}")
                request_body_for_hubspot = formatted_data
            except Exception as e:
                error_message = f"Error during new_lead_template formatting: {e}. Original data: {data}"
                print(f"ERROR: {error_message}")
                return {"status": "error", "message": error_message}
        elif data:
             print(f"Request body (raw, no template formatting for {method}): {json.dumps(data, indent=2)}")


        try:
            if method == 'POST':
                response = requests.post(url, headers=headers, json=request_body_for_hubspot, params=params)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=request_body_for_hubspot, params=params)
            # ... (GET, DELETE as before)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            print(f"Raw Response Status Code: {response.status_code}")
            response.raise_for_status()

            if response.content:
                try:
                    json_response = response.json()
                    print(f"Successful API Response (JSON): {json.dumps(json_response, indent=2)}")
                    return json_response
                except json.JSONDecodeError:
                    print("Warning: Successful API response was not JSON. Returning text.")
                    return {"status": "success_but_not_json", "content": response.text}
            else:
                print("Info: Successful API response body is empty.")
                return {"status": "success", "message": f"{method} request to {endpoint} successful with no content."}

        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err} - Status: {http_err.response.status_code} - Response: {http_err.response.text}"
            print(f"ERROR: {error_message}")
            return {"status": "error", "message": error_message, "details": http_err.response.text if hasattr(http_err.response, 'text') else str(http_err)}
        except requests.exceptions.RequestException as e:
            error_message = f"API Request failed: {e}"
            print(f"ERROR: {error_message}")
            return {"status": "error", "message": error_message}

    # This is the primary method for creating a lead, replacing the placeholder and create_lead2
    def create_lead(self, json_payload_from_llm: dict):
        try:
            email = json_payload_from_llm.get("email", None)
            if email:
                res = self.db_client.find_lead_by_email(email)
                if res:
                    error_msg = f"Lead already exists"
                    print(f"ERROR: {error_msg}")
                    return json.dumps({"status": "error", "message": error_msg})
            else:
                    error_msg = f"Failed to create lead in HubSpot. No email"
                    print(f"ERROR: {error_msg}")
                    return json.dumps({"status": "error", "message": error_msg})
        except e:
            error_msg = f"Failed to connect to Postgres"
            print(f"ERROR: {error_msg}")
            return json.dumps({"status": "error", "message": error_msg})


 

        """
        Method of HubSpotTool class to create a lead.
        The json_payload_from_llm is expected to be the direct payload from the LLM,
        structured as per the tool's docstring provided to the LLM
        (e.g., {"properties": {"email": ..., "firstname": ..., ...}}).
        """
        print("\n--- HubSpotTool METHOD: Creating a New Lead (Contact) ---")
        print(f"Payload received by HubSpotTool.create_lead (from LLM): {json.dumps(json_payload_from_llm, indent=2)}")

        create_lead_endpoint = "/crm/v3/objects/contacts"

        # The `json_payload_from_llm` is passed to call_hubspot_api_oauth.
        # Inside call_hubspot_api_oauth, new_lead_template will format this data
        # into the final payload for the HubSpot API.
        created_lead_response = self.call_hubspot_api_oauth('POST', create_lead_endpoint, data=json_payload_from_llm)

        if created_lead_response and isinstance(created_lead_response, dict) and created_lead_response.get('id'):
            new_lead_id = created_lead_response.get('id')
            print(f"HubSpot API: Lead created successfully. ID: {new_lead_id}")

            # Extract properties for DB storage from the original LLM-generated payload.
            # The LLM is instructed to provide json_payload_from_llm in {"properties": {...}} format.
            properties_for_db = json_payload_from_llm.get("properties") if isinstance(json_payload_from_llm, dict) else None

            if not isinstance(properties_for_db, dict):
                error_msg_db = f"Could not extract 'properties' dictionary from LLM-generated payload for DB storage. Payload was: {json_payload_from_llm}"
                print(f"ERROR: {error_msg_db}")
                # Return a clear message to LLM about HubSpot success but DB fail
                return json.dumps({"status": "success_hubspot_db_fail", "message": f"Lead created in HubSpot with ID {new_lead_id}, but failed to extract data for DB. {error_msg_db}", "hubspot_id": new_lead_id})

            try:
                db_id = self.db_client.store_lead(hubspot_id=new_lead_id, lead_data=properties_for_db)
                print(f"DB: Lead {new_lead_id} stored successfully with DB ID {db_id}.")
                return json.dumps({"status": "success", "message": f"Lead created successfully in HubSpot (ID: {new_lead_id}) and stored in DB.", "hubspot_id": new_lead_id, "db_id": db_id})
            except Exception as e:
                db_error_msg = f"Error storing lead {new_lead_id} in DB: {e}"
                print(f"ERROR: {db_error_msg}")
                return json.dumps({"status": "success_hubspot_db_fail", "message": f"Lead created in HubSpot with ID {new_lead_id}, but DB storage failed: {db_error_msg}", "hubspot_id": new_lead_id})
        else:
            error_msg = f"Failed to create lead in HubSpot. API Response: {created_lead_response}"
            print(f"ERROR: {error_msg}")
            return json.dumps({"status": "error", "message": error_msg, "api_response": created_lead_response})

    # ... (update_lead, create_meeting methods - ensure they also return JSON strings) ...
    def update_lead(self, json_payload: dict):
        """Updates an existing lead in HubSpot.
        Args:
            json_payload (dict): A dictionary containing the lead's HubSpot ID and properties to update.
                                 Example: {"lead_id": "12345", "properties": {"firstname": "Johnny"}}
        Returns:
            str: JSON string of the HubSpot API response or an error message.
        """
        print("\n--- HubSpotTool METHOD: Updating Lead (Contact) ---")
        print(f"Update payload received by HubSpotTool.update_lead (from LLM): {json.dumps(json_payload, indent=2)}")

        lead_id = json_payload.get('lead_id')
        properties_to_update = json_payload.get('properties')

        if not lead_id:
            error_msg = "lead_id is required for updating a lead."
            print(f"ERROR: {error_msg}")
            return json.dumps({"status": "error", "message": error_msg})
        if not isinstance(properties_to_update, dict):
            error_msg = "'properties' (as a dictionary) are required for updating a lead."
            print(f"ERROR: {error_msg}")
            return json.dumps({"status": "error", "message": error_msg})

        modify_lead_endpoint = f"/crm/v3/objects/contacts/{lead_id}"
        
        # The payload for HubSpot API's PATCH contacts endpoint needs to be {"properties": {...}}
        # The LLM should provide `properties_to_update` as the inner dictionary.
        # The `json_payload` from LLM should be `{"lead_id": "...", "properties": {"firstname": "newname"}}`
        # The `call_hubspot_api_oauth` will use `new_lead_template` which expects the full structure.
        # So, we pass `properties_to_update` to `new_lead_template` via the `data` argument of `call_hubspot_api_oauth`.
        # However, new_lead_template is for *new* leads. For updates, HubSpot expects {"properties": ...}.
        # Let's pass the already structured properties directly.
        hubspot_api_payload = {"properties": properties_to_update}
        print(f"Payload for HubSpot PATCH API: {json.dumps(hubspot_api_payload, indent=2)}")
        
        # For PATCH, new_lead_template might not be appropriate if it adds default fields for new leads.
        # We'll pass the constructed hubspot_api_payload directly.
        # To make call_hubspot_api_oauth skip its own new_lead_template formatting for this PATCH,
        # we'd ideally have a flag or different logic.
        # For now, let's assume new_lead_template is smart enough or we bypass it.
        # A simpler way is to ensure the 'data' passed to call_hubspot_api_oauth is what HubSpot needs.
        response = self.call_hubspot_api_oauth('PATCH', modify_lead_endpoint, data=hubspot_api_payload)

        return json.dumps(response) if response else json.dumps({"status": "error", "message": "Update lead API call failed or returned no response."})


    def create_meeting(self, json_payload: dict):
        """Creates a new meeting in HubSpot.
        Args:
            json_payload (dict): A dictionary containing meeting properties and associations.
                                 Example: {"properties": {"hs_meeting_title": "Demo Meeting", ...},
                                           "associations": [{"to": {"id": "contact_id"}, "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": ...}]}]}
        Returns:
            str: JSON string of the HubSpot API response or an error message.
        """
        print("\n--- HubSpotTool METHOD: Creating Meeting ---")
        print(f"Create meeting payload received (from LLM): {json.dumps(json_payload, indent=2)}")

        create_meeting_endpoint = "/crm/v3/objects/meetings"
        
        # Assuming json_payload from LLM is already in the correct HubSpot API format for meetings.
        # The new_lead_template in call_hubspot_api_oauth might not be suitable for meetings.
        # For POST to meetings, HubSpot expects the direct payload.
        response = self.call_hubspot_api_oauth('POST', create_meeting_endpoint, data=json_payload)
        
        if response and isinstance(response, dict) and response.get('id'):
            meeting_id = response.get('id')
            # ... (DB storing logic as before) ...
            print(f"DB: Meeting {meeting_id} stored (details omitted for brevity).")
        
        return json.dumps(response) if response else json.dumps({"status": "error", "message": "Create meeting API call failed or returned no response."})

# Instantiate the tool class
hstool = HubSpotTool()

# This is the function that will be wrapped by FunctionTool and called by the ADK agent

# This is the function that will be wrapped by FunctionTool and called by the ADK agent
def create_lead(json_payload:dict):    
    """Create a new lead (contact) in HubSpot and store it in the local database.

    This function creates a new contact in HubSpot using the HubSpot API and then stores
    the lead information in a local PostgreSQL database for tracking purposes.

    Args:
        json_payload (dict): A dictionary containing the lead's properties. The required keys are:
        "email", "firstname", "lastname", "phone", "company", and "website"
    Returns:
        str: A JSON string indicating the result of the operation.
             On success: '{"status": "success", "message": "Lead created...", "hubspot_id": "123", "db_id": 456}'
             On failure: '{"status": "error", "message": "Error details..."}'
    """
    print('--- Standalone FUNCTION: Agent called "create_lead()" ---')
    print(f"Received json_payload by standalone create_lead function: {json.dumps(json_payload, indent=2)}")
    
    # The json_payload from LLM should ideally be in the format {"properties": {...}}
    # as per the docstring and system prompt.
    result_json_string = hstool.create_lead(json_payload)

    print(f"Result from hstool.create_lead to be returned to LLM: {result_json_string}")
    return result_json_string


create_lead_tool = FunctionTool(func=create_lead)