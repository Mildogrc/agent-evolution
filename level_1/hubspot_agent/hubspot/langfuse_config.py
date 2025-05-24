from langfuse import Langfuse
import os

# Initialize Langfuse client for local instance
langfuse = Langfuse(
    public_key="pk-lf-1234567890",  # This can be any string for local development
    secret_key="sk-lf-1234567890",  # This can be any string for local development
    host="http://localhost:3000"     # Local Langfuse instance
)

def get_langfuse_client():
    return langfuse 