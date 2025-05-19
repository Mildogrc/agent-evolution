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

    class Config:
        # This allows FastAPI to show example values in the documentation
        json_schema_extra = {
            "example": {
                "sender": "jane.doe@example.com",
                "recipient": "support@example.com",
                "subject": "Inquiry about product X",
                "body": "Dear Support Team,\n\nI have a question regarding product X. Could you please provide more details on its features?\n\nThanks,\nJane",
                "received_at": "2024-05-18T10:00:00Z",
                "message_id": "<somerandomid123@mail.example.com>"
            }
        }

# Initialize ADK App with your root agent
# Ensure root_agent is correctly defined and imported
try:
    adk_app = AdkApp(agent=root_agent)
except Exception as e:
    print(f"Error initializing AdkApp with root_agent: {e}")
    # Handle this critical error appropriately, as the app won't function
    adk_app = None # Set to None to prevent further errors if initialization fails



@app.post("/chat")
async def chat_with_agent(query: str):

    session = adk_app.create_session()
    response_events = []
    async for event in session.execute(input={"message": query}):
        response_events.append(event)
        if event.name == "agent:llm:final_response": 
            return {"response": event.data.get("text")}
    return {"response_events": response_events} # Fallback


# --- New Endpoint for Processing Email Content ---
@app.post("/process-email", tags=["Agent Interaction"])
async def process_email_with_agent(email_data: EmailContent):
    if not adk_app:
        raise HTTPException(status_code=500, detail="ADK Application not initialized.")

    try:
        session = adk_app.create_session() # Consider if session management is needed per email or per sender
        response_events = []
        final_text_response = None

        async for event in session.execute(input={"message": system_prompt}):
            response_events.append(event.model_dump_json()) # Storing JSON serializable event data
            if event.name == "agent:llm:final_response":
                final_text_response = event.data.get("text")
                return {
                    "status": "Email processed",
                    "agent_response": final_text_response,
                    "original_subject": email_data.subject,
                    "original_sender": email_data.sender,
                    "session_id": session.session_id
                }
        
        # Fallback if no 'agent:llm:final_response' event with text was found
        # This logic mirrors the /chat endpoint's fallback
        if final_text_response:
             return {"status": "Email processed", "agent_response": final_text_response, "session_id": session.session_id}

        return {
            "status": "Email processed, but no direct text response from agent.",
            "agent_response_summary": "Agent processed the email content.",
            "all_events": response_events, # Be cautious with returning all events in production
            "session_id": session.session_id
        }

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