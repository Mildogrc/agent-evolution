import dotenv # Good practice if your config relies on .env files
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field # For data validation
from typing import Optional
import datetime

# Assuming hubspot.agent and hubspot.config are your custom modules
from hubspot.agent import root_agent, system_prompt
from hubspot.config import Config

import vertexai
from vertexai.preview.reasoning_engines import AdkApp

# Initialize Vertex AI (ensure Config.gcp["gcp_project"] is correctly loaded)
# It's good practice to load .env files before accessing Config if it uses them
dotenv.load_dotenv() # Load .env file if present

try:
    vertexai.init(project=Config.gcp["gcp_project"])
except Exception as e:
    print(f"Error initializing Vertex AI: {e}")
    # Depending on your needs, you might want to exit or handle this gracefully
    # For now, we'll let it proceed so FastAPI can start, but agent calls might fail.

app = FastAPI(
    title="ADK Agent API",
    description="API to interact with the ADK agent for chat and email processing.",
    version="1.0.0"
)

# --- Pydantic Model for Incoming Email Data ---
class EmailContent(BaseModel):
    sender: EmailStr = Field(..., example="sender@example.com", description="Email address of the sender.")
    recipient: Optional[EmailStr] = Field(None, example="recipient@example.com", description="Email address of the recipient (if available).")
    subject: str = Field(..., example="Important Update", description="Subject line of the email.")
    body: str = Field(..., example="Hello team, here's an update...", description="Main content/body of the email.")
    received_at: Optional[datetime.datetime] = Field(None, example="2024-05-18T14:30:00Z", description="Timestamp when the email was received.")
    message_id: Optional[str] = Field(None, example="<unique-message-id@mail.example.com>", description="Unique identifier for the email message.")
    session_id: Optional[str] = Field(None, example="<session-id@mail.example.com>", description="Unique identifier for the email session.")
    user_id: str = Field(..., example="user123", description="Unique identifier for the user.")

    class Config:
        # This allows FastAPI to show example values in the documentation
        json_schema_extra = {
            "example": {
                "sender": "jane.doe@example.com",
                "recipient": "support@example.com",
                "subject": "Inquiry about product X",
                "body": "Dear Support Team,\n\nI have a question regarding product X. Could you please provide more details on its features?\n\nThanks,\nJane",
                "received_at": "2024-05-18T10:00:00Z",
                "message_id": "<somerandomid123@mail.example.com>",
                "session_id": "<somerandomid123@mail.example.com>",
                "user_id": "user123"
            }
        }
        
try:
    adk_app = AdkApp(agent=root_agent)
    print("ADK Agent started!")
except Exception as e:
    print(f"Error initializing AdkApp with root_agent: {e}")
    # Handle this critical error appropriately, as the app won't function
    adk_app = None # Set to None to prevent further errors if initialization fails




# --- New Endpoint for Processing Email Content ---
@app.post("/process-email", tags=["Agent Interaction"])
async def process_email_with_agent(email_data: EmailContent):
    print('Processing: ', email_data)
    if not adk_app:
        raise HTTPException(status_code=500, detail="ADK Application not initialized.")

    try:
        # Use provided session_id if available, otherwise create new session
        session = adk_app.create_session(user_id=email_data.sender, session_id=email_data.session_id)
        print(f"Sending to agent (session {session}): {email_data.body}")

        

        full_response_text = ""
        final_response_event_data = None
        
        async for event in adk_app.stream_query(message=email_data.body, user_id=email_data.sender, session=session):
            print(f"Received event: {event.name}, Data: {event.data}") # Log all events for debugging

            if event.name == "agent:llm:chunk": # Streaming text from the LLM
                if "text" in event.data:
                    chunk_text = event.data["text"]
                    print(chunk_text, end="", flush=True) # Print chunks as they arrive
                    full_response_text += chunk_text
            elif event.name == "agent:llm:final_response": # A consolidated final response from the LLM
                if "text" in event.data:
                    # If we haven't built up text from chunks, use this
                    if not full_response_text:
                        full_response_text = event.data["text"]
                    final_response_event_data = event.data # Store the whole final response data
                    print(f"\nFinal response event data: {final_response_event_data}") # Newline after chunks
                break # Often, the final_response event is the last one you need for the text output
            elif event.name == "agent:error":
                print(f"\nAgent error: {event.data.get('message')}")
                # Handle error appropriately
                return f"Agent error: {event.data.get('message')}"
            # You can handle other event types here (e.g., tool calls) if needed



    except Exception as e:
        # Log the exception for debugging
        print(f"Error processing email with agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error during email processing with agent: {str(e)}")

# --- Optional: Root endpoint for health check or API info ---
@app.get("/", tags=["General"])
async def read_root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "message": "Welcome to the ADK Agent API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }