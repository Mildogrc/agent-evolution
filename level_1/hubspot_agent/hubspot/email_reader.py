import imaplib
import email
import os
from hubspot.config import Config
import keyring

# Assuming you have a function to process the email content with your agent
# from hubspot.agent import process_email_with_agent

# Email server details
IMAP_SERVER = Config.email["imap_server"]
EMAIL_ADDRESS = Config.email["email_address"]
EMAIL_PASSWORD = keyring.get_password(Config.hubspot["service_id"], Config.email["email_password"]) 

def get_email_body(email_message: email.message.Message) -> str:
    """Extract email body content"""
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if "attachment" not in content_disposition:
                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode()
                    except:
                        body += part.get_payload()
    else:
        try:
            body = email_message.get_payload(decode=True).decode()
        except:
            body = email_message.get_payload()
    return body


def fetch_emails(count = 10, search_param='(UNSEEN)'):
    """Fetches unread emails from the configured IMAP server."""
    try:

        ret = []

        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select('inbox') # Select the inbox


        # Search for unread emails
        status, messages = mail.search(None, search_param)
        if status == 'OK':
            email_ids = messages[0].split()
            
            if count:
                email_ids = email_ids[-count:]
            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
 

                    print(f"Processing email from: {msg['from']}")
                    msg_data = {
                        "sender": msg['From'],
                        "recipient": msg['To'],
                        "subject": msg['Subject'],
                        "body": get_email_body(msg),
                        "received_at": msg['Date'],
                        "message_id": msg['Message-ID']
                    }
                    ret.append(msg_data)

        return ret
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []
    finally:
        if mail:
            mail.logout()


if __name__ == "__main__":
    # Example usage: Call fetch_emails() to retrieve and process emails
    ret = fetch_emails(1, '(ALL)')
    print(ret)
