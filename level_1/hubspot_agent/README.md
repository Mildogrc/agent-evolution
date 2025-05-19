# Project Title

This is an implementation of an AI agent (backed by LLM) that uses Google ADK and an LLM to parse an email, identify if it is a lead, and adds it to HubSpot. It also uses Postgres database to maintain leads and uses Langfuse for logging and tracing

## Prerequisites

Before you begin, ensure you have the following installed:

*   Python 3.8 or higher
*   pip (Python package installer)
*   Docker and Docker Compose
*   keyring (for secure credential storage)

## Setup

1.  **Clone the repository (if applicable):**

    ```bash
    # Replace with your repository URL
    # git clone <repository_url>
    # cd <repository_directory>
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv .venv
    # On Windows:
    # .venv\Scripts\activate
    # On macOS/Linux:
    # source .venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up secure credentials:**

    This project uses `keyring` to securely store sensitive information like API tokens and database passwords. Run the `Secrets.py` script to set up your credentials.

    ```bash
    python hubspot/Secrets.py
    ```

    Follow the prompts to enter your HubSpot access token and database credentials. These will be stored securely by your operating system's credential manager.

5.  **Set up local Langfuse and PostgreSQL:**

    This project uses a local instance of Langfuse and PostgreSQL for observability and data storage, managed by Docker Compose. Ensure Docker is running.

    Create a `.env` file in the project root directory with the following content (adjust values as needed, but match those used in `docker-compose.yml` and `hubspot/langfuse_config.py` for the local setup):

    ```dotenv
    POSTGRES_USER=<postgres-user-name>
    POSTGRES_PASSWORD=<postgres-password>
    POSTGRES_DB=<postgres-database-name>
    ```

    Start the Docker containers:

    ```bash
    docker-compose up -d
    ```

    This will start the PostgreSQL database and the Langfuse server. You can access the Langfuse UI at `http://localhost:3000`.

## Running the Agent

1.  Ensure your virtual environment is active.
2.  Ensure your local Langfuse and PostgreSQL containers are running (`docker-compose up -d`).
3.  Two options to run the agent 
    * **Using the `adk web` command:**
        ```
        adk web --port 8080
        ```
        The agent web server will start and be accessible at `http://localhost:8080`.

    * **Using the adk app**
        ```
        uvicorn adk_agent:app --reload
        ```

## Langfuse Observability

This project is integrated with Langfuse to provide observability for the agent's behavior and interactions with external services (like HubSpot). All traces and logs will be sent to your local Langfuse instance.

*   View traces, spans, and logs in the Langfuse UI at `http://localhost:3000`.
