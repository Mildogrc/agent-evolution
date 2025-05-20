import imaplib
import email
import os
from config import Config
import keyring

# Assuming you have a function to process the email content with your agent
# from hubspot.agent import process_email_with_agent

# Email server details
IMAP_SERVER = Config.email["imap_server"]
EMAIL_ADDRESS = Config.email["email_address"]
EMAIL_PASSWORD = keyring.get_password(Config.hubspot["service_id"], Config.email["email_password"]) 

def fetch_emails():
    """Fetches unread emails from the configured IMAP server."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select('inbox') # Select the inbox

        # Search for unread emails
        status, email_ids = mail.search(None, '(UNSEEN)')
        if status == 'OK':
            for email_id in email_ids[0].split():
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Process the email message
                    # You would extract relevant parts (body, etc.) and
                    # pass it to your agent's processing function
                    print(f"Processing email from: {msg['from']}")
                    # process_email_with_agent(msg) # Call your agent processing function

        mail.logout()
    except Exception as e:
        print(f"Error fetching emails: {e}")

if __name__ == "__main__":
    # Example usage: Call fetch_emails() to retrieve and process emails
    fetch_emails()
