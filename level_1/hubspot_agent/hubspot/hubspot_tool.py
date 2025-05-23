import requests
import json
import datetime
import keyring
from hubspot.config import Config
from hubspot.postgres_client import PostgresClient
from langfuse.decorators import langfuse_context, observe
from google.adk.agents import Agent
from hubspot.langfuse_config import get_langfuse_client
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool

class HubSpotTool():
    """Class to interact with the HubSpot API"""

    def __init__(self, base_url=None):
        self.BASE_URL = base_url or Config.hubspot["base_url"]

        # Get configuration from config.py
        service_id = Config.hubspot["service_id"]
        access_token_key = Config.hubspot["access_token_key"]
        db_user_key = Config.database["db_user_key"]
        db_password_key = Config.database["db_password_key"]

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
        span = langfuse_context.get_current_observation()
        if span:
            span.log(key="api_call_details", value={
                "message": "Calling API",
                "endpoint": endpoint,
                "method": method,
                "payload": data
            })

        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        print(f"Making {method} request to {url}")
        span = langfuse_context.get_current_observation()
        if span:
            span.log(key="http_request", value={
                "message": f"Making {method} request to {url}"
            })
        if params:
            print(f"Query parameters: {params}")
            span = langfuse_context.get_current_observation()
            if span:
                span.log(key="query_parameters", value=params)
        if data:
            print(f"Request body: {json.dumps(data, indent=2)}")
            span = langfuse_context.get_current_observation()
            if span:
                span.log(key="request_body", value=json.dumps(data, indent=2))

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
            span = langfuse_context.get_current_observation()
            if span:
                span.log(key="response_status", value=response.status_code)
            # Attempt to parse JSON response if content exists
            if response.content:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    print("Warning: Response was not JSON.")
                    span = langfuse_context.get_current_observation()
                    if span:
                        span.log(key="json_decode_warning", value="Response was not JSON")
                    return response.text  # Return plain text if not JSON
            else:
                print("Info: Response body is empty.")
                span = langfuse_context.get_current_observation()
                if span:
                    span.log(key="empty_response_body", value="Response body is empty")
                return None  # No content in response

        except requests.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            span = langfuse_context.get_current_observation()
            if span:
                 span.log(key="api_request_failed", value=str(e), level="ERROR")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                span = langfuse_context.get_current_observation()
                if span:
                    span.log(key="failed_response_status", value=e.response.status_code, level="ERROR")
                print(f"Response Body: {e.response.text}")
                span = langfuse_context.get_current_observation()
                if span:
                    span.log(key="failed_response_body", value=e.response.text, level="ERROR")
            return None

    def delete_lead(self, lead_id):
        """Delete a lead from HubSpot"""
        delete_lead_endpoint = f"/crm/v3/objects/contacts/{lead_id}"
        return self.call_hubspot_api_oauth(method='DELETE', endpoint=delete_lead_endpoint)

    def create_lead(self, lead_data: dict):
        # Example 1: Creating a new lead
        print("\n--- Creating a New Lead (Contact) using Private App Token ---")
        span = langfuse_context.get_current_observation()
        if span:
            span.log(key="create_lead_start", value="Creating a New Lead (Contact) using Private App Token")
        print(f"Lead data received: {json.dumps(lead_data, indent=2)}")
        span = langfuse_context.get_current_observation()
        if span:
            span.log(key="lead_data_received", value=json.dumps(lead_data, indent=2))
        """Create a new lead in HubSpot"""
        create_lead_endpoint = "/crm/v3/objects/contacts"
        
        # Add Langfuse span for the API call
        span = langfuse_context.get_current_observation()
        if span:
             with span.span(name="hubspot-api-create-lead", input=lead_data, metadata={"endpoint": create_lead_endpoint, "method": "POST"}) as api_span:
                created_lead_response = self.call_hubspot_api_oauth('POST', create_lead_endpoint, data=lead_data)
                api_span.update(output=created_lead_response)
        else:
             # If there's no active span, just call the API without tracing
             created_lead_response = self.call_hubspot_api_oauth('POST', create_lead_endpoint, data=lead_data)

        if created_lead_response:
            print("Lead created successfully using Private App Token:")
            span = langfuse_context.get_current_observation()
            if span:
                span.log(key="create_lead_success", value="Lead created successfully using Private App Token")
            print(json.dumps(created_lead_response, indent=2))
            span = langfuse_context.get_current_observation()
            if span:
                span.log(key="created_lead_response", value=json.dumps(created_lead_response, indent=2))
            new_lead_id = created_lead_response.get('id')
            print(f"Newly created lead ID: {new_lead_id}")
            span = langfuse_context.get_current_observation()
            if span:
                span.log(key="new_lead_id", value=new_lead_id)

            try:
                # Store the lead in PostgreSQL if created successfully
                db_id = self.db_client.store_lead(hubspot_id=new_lead_id, lead_data=lead_data)
            finally:
                return new_lead_id
        else:
            print("Failed to create lead using Private App Token.")
            span = langfuse_context.get_current_observation()
            if span:
                span.log(key="create_lead_failed", value="Failed to create lead using Private App Token", level="ERROR")
            return None

    def update_lead(self, properties: json):
        lead_id = properties.get('lead_id')
        """Update an existing lead in HubSpot"""
        modify_lead_endpoint = f"/crm/v3/objects/contacts/{lead_id}"
        # Get current span for logging within this method
        span = langfuse_context.get_current_observation()
        if span:
            span.log(key="update_lead_start", value={
                "message": "Updating Lead",
                "lead_id": lead_id,
                "properties": properties
            })
        response = self.call_hubspot_api_oauth('PATCH', modify_lead_endpoint, data=properties)
        span = langfuse_context.get_current_observation()
        if span:
            span.log(key="update_lead_response", value=response)
        return response

    def create_meeting(self, meeting_data: json):
        """Create a new meeting in HubSpot"""
        create_meeting_endpoint = "/crm/v3/objects/meetings"
        # Get current span for logging within this method
        span = langfuse_context.get_current_observation()
        if span:
             span.log(key="create_meeting_start", value={
                 "message": "Creating Meeting",
                 "meeting_data": meeting_data
             })
        response = self.call_hubspot_api_oauth('POST', create_meeting_endpoint, data=meeting_data)
        span = langfuse_context.get_current_observation()
        if span:
             span.log(key="create_meeting_response", value=response)
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
            span = langfuse_context.get_current_observation()
            if span:
                span.log(key="meeting_stored_in_db", value={
                    "meeting_id": meeting_id,
                    "lead_id": lead_id,
                    "db_id": db_meeting_id
                })

        return response

hstool = HubSpotTool()


def create_lead(json_payload:dict):    
    """Create a new lead (contact) in HubSpot and store it in the local database.

    This function creates a new contact in HubSpot using the HubSpot API and then stores
    the lead information in a local PostgreSQL database for tracking purposes.

    Args:
        lead_data (dict): A dictionary containing the lead's properties. The dictionary should
            follow HubSpot's contact properties format. Example:
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

    Raises:
        requests.exceptions.RequestException: If the API call to HubSpot fails.
        Exception: If there's an error storing the lead in the local database.

    Note:
        - The function uses the HubSpot Private App Token for authentication
        - All API calls and database operations are logged using Langfuse for observability
        - The lead is stored in both HubSpot and a local PostgreSQL database
    """
    print('Agent called "create_lead()"')
    span = langfuse_context.get_current_observation()
    if span:
        span.log(key="agent_create_lead_called", value="Agent called create_lead()")
    return hstool.create_lead(json_payload)

create_lead_tool = FunctionTool(func=create_lead)
# , name="create_lead", description="Create a new lead (contact) in HubSpot and store it in the local database.")