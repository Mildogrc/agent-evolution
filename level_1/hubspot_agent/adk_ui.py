import streamlit as st
import requests
import json
from datetime import datetime
import time
import sys
from hubspot.email_reader import fetch_emails
import email.utils
import dateutil.parser

# Print debug information
print("Starting Streamlit app...")


# Constants
API_BASE_URL = "http://localhost:8000"  # Update this if your FastAPI server runs on a different port


class ADKAgentUI:
    def __init__(self):
        self.session_id = None
        self.is_running = False
        self.emails = fetch_emails(search_param='(ALL)')
        self.user_id = "default_user"  # You might want to make this configurable

    def get_emails(self):
        return self.emails
        
    def check_agent(self):
        try:
            response = requests.get(f"{API_BASE_URL}/")
            print("Is agent running?", response)
            if response.status_code == 200:
                self.is_running = True
                return True, "Agent is running!"
            return False, "Agent is not running"
        except Exception as e:
            return False, f"Agent is not running"
    
    def send_message(self, message):
        if not self.is_running:
            return False, "Agent is not running"
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json={"query": message}
            )
            if response.status_code == 200:
                return True, response.json()["response"]
            return False, f"Error: {response.text}"
        except Exception as e:
            return False, f"Error sending message: {str(e)}"
    
    def send_email(self, sender, recipient, subject, body, received_at, message_id):
        if not self.is_running and self.check_agent():
            return False, "Agent is not running"
        
        try:
            # Parse the received_at string into a datetime object if it's a string
            if isinstance(received_at, str):
                try:
                    # Try parsing RFC 2822 format first
                    parsed_date = email.utils.parsedate_to_datetime(received_at)
                except:
                    # Fallback to dateutil parser for other formats
                    parsed_date = dateutil.parser.parse(received_at)
                received_at = parsed_date.isoformat()
            
            # Format email data according to EmailContent model
            email_data = {
                "sender": sender,
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "received_at": received_at,
                "message_id": message_id,
                "session_id": self.session_id,  # Include the session ID
                "user_id": self.user_id  # Include the user ID
            }
            
            print("Sending email data:", email_data)  # Debug print
            
            response = requests.post(
                f"{API_BASE_URL}/process-email",
                json=email_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # Update session ID from response if provided
                if 'session_id' in response_data:
                    self.session_id = response_data['session_id']
                return True, response_data
            elif response.status_code == 422:
                error_detail = response.json().get('detail', 'Validation error')
                return False, f"Validation error: {error_detail}"
            else:
                return False, f"Error: {response.text}"
        except Exception as e:
            return False, f"Error processing email: {str(e)}"



try:
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = ADKAgentUI()
    if 'selected_emails' not in st.session_state:
        st.session_state.selected_emails = st.session_state.agent.get_emails()

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.error("Please check if the FastAPI server is running at " + API_BASE_URL)



st.set_page_config(
    page_title="ADK Agent Control Panel",
    page_icon="🤖",
    layout="wide"
)


# Agent Status
st.header("Agent Controls")
status_color = "green" if st.session_state.agent.is_running else "red"
st.markdown(f"Status: <span style='color:{status_color}'>{'Running' if st.session_state.agent.is_running else 'Stopped'}</span>", unsafe_allow_html=True)





# Email Processing
st.header("Email Processing")
with st.expander("Fetched Emails", expanded=True):
    if st.session_state.selected_emails:
        
        # Create a table with buttons
        st.markdown("""
        <style>
        .stButton button {
            width: 100%;
            padding: 0;
            margin: 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Table header
        cols = st.columns([0.05, 0.25, 0.55, 0.15])
        cols[0].write("Action")
        cols[1].write("Sender")
        cols[2].write("Subject")
        cols[3].write("Date")
        
        # Table rows
        for idx, email in enumerate(st.session_state.selected_emails):
            cols = st.columns([0.05, 0.25, 0.55, 0.15])
            
            # Button column
            msg_id = email.get('message_id', '')
            subject = email.get('subject', '')
            sender = email.get('sender', '')
            body = email.get('body', '')
            recipient = email.get('recipient', '')
            sent_at = email.get('received_at', datetime.now())


            
            if cols[0].button("🤖", key=msg_id):
                status, resp = st.session_state.agent.send_email(sender=sender, subject=subject, recipient=recipient, body=body, received_at=sent_at, message_id=msg_id)
                
                # Show status and response in sidebar
                with st.sidebar:
                    if status:
                        st.success("Message processed successfully!")
                        st.json(resp)
                    else:
                        st.error("Failed to process message")
                        st.error(resp)
            
            # Data columns
            cols[1].write(sender)
            cols[2].write(subject)
            cols[3].write(email.get('received_at', ''))
        
        # Show selected emails count
        if st.session_state.selected_emails:
            st.write(f"Selected emails: {len(st.session_state.selected_emails)}")
    else:
        st.info("No emails found.")

try:
    # Test if we can make a request to the API
    response = requests.get(f"{API_BASE_URL}/")
    st.success(f"API Connection Test: {response.status_code}")
except Exception as e:
    st.error(f"API Connection Error: {str(e)}")

