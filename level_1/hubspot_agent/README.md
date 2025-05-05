## HubSpot Agent using Google ADK
This agent integrates with HubSpot using HubSpot APIs, and is capable of automatically parsing emails to manage contacts using the email content.

### Key Features
The agent can create a new lead in HubSpot extracting the contents of the email, update the info about the lead if already existing, set up meetings with leads and other basic activities.

### Implementation Details
The agent was implemented using Google ADK and tested with Gemini 2.0 Flash as the LLM. The agent, defined in `hubspot/agent.py`, contains the prompt and refers to the HubSpot client tool. The tool, defined in `hubspot/hubspot_tool.py`, invokes HubSpot API to manage leads and meetings. The tool also stores the `lead_id` created by HubSpot, along with `name` and `email` of the lead.

### How to run
The setup is similar to as defined in [Google ADK Quickstart guide](https://google.github.io/adk-docs/get-started/quickstart/). 
1. Run `python -m env .env` from the project root folder (folder named `hubspot_agent` if you checked out the git project)
2. Run `python hubspot/Secrets.py` to setup your HubSpot and DB credentials 
3. Update `hubspot/.env` file with your Google API key (you can create one [here](https://aistudio.google.com/app/apikey))
4. Start the agent with `adk web` from the project root folder
5. Open [http://localhost:8000](http://localhost:8000) from your browser

### Common errors
1. If you have trouble running on Windows machines, try an alternate port. For instance, you can use port `8080` with command `adk web --port 8080`. Navigate to [http://localhost:8080](http://localhost:8080)