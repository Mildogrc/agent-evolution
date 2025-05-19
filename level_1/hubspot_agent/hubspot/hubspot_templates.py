import datetime
import json

from hubspot.hubspot_tool import HubSpotTool
from hubspot.langfuse_config import create_trace


class HubSpotTemplates:
    """Class to store JSON templates for HubSpot API requests"""

    @staticmethod
    def new_lead_template(email, firstname, lastname, phone, company, website):
        return {
            "properties": {
                "email": email,
                "firstname": firstname,
                "lastname": lastname,
                "phone": phone,
                "company": company,
                "website": website,
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


def main():

    # Create a trace for the entire agent flow
    with create_trace("hubspot_agent_flow", metadata={"source": "manual_run"}) as trace:

        # Initialize HubSpot and PostgreSQL clients
        hs_tool = HubSpotTool()
        lead_data = HubSpotTemplates.new_lead_template(
            email="new.lead.private.app@example.com",
            firstname="App",
            lastname="Lead",
            phone="111-222-3333",
            company="App Integrations Inc.",
            website="https://www.appintegrations.com"
        )

        # Create a span for new lead creation
        with trace.span(
            name="create_lead_process",
            input=lead_data,
            metadata={"step": "initial_creation"}
        ) as create_span:
            new_lead_id = hs_tool.create_lead(lead_data)
            create_span.update(output=new_lead_id, metadata={
                "step": "initial_creation", "status": "success" if new_lead_id else "failed"}
            )

        if new_lead_id:

            # Example 2: Updating the lead
            print(f"\n--- Modifying Lead with ID: {new_lead_id} using Private App Token ---")
            updated_properties = HubSpotTemplates.update_lead_template(
                phone="444-555-6666",
                state="NY",
                lead_status="Open"
            )

            # Create a span for updating the lead
            with trace.span(
                name="update_lead_process",
                input=updated_properties,
                metadata={"step": "update"}
            ) as update_span:
                modified_lead_response = hs_tool.update_lead(
                    lead_id=new_lead_id,
                    properties=updated_properties
                )
                update_span.update(output=modified_lead_response, metadata={
                    "step": "update", "status": "success" if modified_lead_response else "failed"}
                )

            if modified_lead_response:
                print("Lead modified successfully using Private App Token:")
                print(json.dumps(modified_lead_response, indent=2))
            else:
                print("Failed to modify lead using Private App Token.")

            # Example 3: Creating a meeting
            print(f"\n--- Creating a Meeting associated with Lead ID: {new_lead_id} using Private App Token ---")

            now = datetime.datetime.now(datetime.timezone.utc)
            start_time = now.isoformat()
            end_time = (now + datetime.timedelta(minutes=30)).isoformat()  # Meeting for 30 mins

            meeting_data = HubSpotTemplates.meeting_template(
                start_time=start_time,
                end_time=end_time,
                lead_id=new_lead_id,
                title="Follow-up Call (App)",
                body="Follow-up discussion via Private App."
            )

            created_meeting_response = hs_tool.create_meeting(meeting_data=meeting_data)

            if created_meeting_response:
                print("Meeting created and associated successfully using Private App Token:")
                print(json.dumps(created_meeting_response, indent=2))

                # Store meeting in database
                meeting_id = created_meeting_response.get('id')

            else:
                print("Failed to create meeting using Private App Token.")
        else:
            print("\nSkipping lead modification and meeting creation as lead creation failed.")

