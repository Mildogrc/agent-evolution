# Standard library imports
import datetime
import json


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

