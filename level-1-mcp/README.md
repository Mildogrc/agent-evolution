# MCP HubSpot Integration with LangChain

This project integrates HubSpot with LangChain using MCP (Machine Control Protocol) to create an AI-powered interface for managing HubSpot leads and contacts.

## Project Structure

```
mcp1/
├── hubspot/
│   └── hubspot_tool.py      # HubSpot API integration tool
├── langchain_agent.py       # LangChain agent using Ollama
├── langchain_mcp_tool.py    # MCP tool for LangChain integration
├── server_ui.py            # Streamlit-based server control UI
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

- HubSpot integration for lead management
- LangChain agent powered by Ollama (llama2)
- Streamlit-based server control interface
- Natural language processing for HubSpot operations

## Prerequisites

1. Python 3.8+
2. Ollama installed (from https://ollama.ai/download)
3. HubSpot API credentials configured
4. llama2 model pulled in Ollama

## Setup

1. Install Ollama and pull the llama2 model:
```bash
ollama pull llama2
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure HubSpot credentials in your keyring:
- Service ID and access token key should be configured in the HubSpot config
- Use keyring to store your HubSpot access token securely

## Running the Application

1. Start the Streamlit server UI:
```bash
streamlit run server_ui.py
```

2. In a separate terminal, you can run the LangChain agent:
```bash
python langchain_agent.py
```

## Usage

### Server UI
The Streamlit UI provides:
- Server start/stop controls
- Status monitoring
- Tool registration information

### LangChain Agent
The agent can handle natural language commands like:
- "Create a new lead for John Smith with email john.smith@example.com"
- "Update the lead with email john.smith@example.com to add phone number 555-0123"
- "Delete the lead with email john.smith@example.com"

### HubSpot Tool
The HubSpot tool provides direct API integration for:
- Creating leads/contacts
- Updating lead information
- Deleting leads
- Creating meetings

## Tools

### MCPTool
- Provides LangChain integration with MCP endpoints
- Handles API communication and error handling
- Supports both synchronous and asynchronous operations

### HubSpotTool
- Manages HubSpot API authentication
- Provides methods for lead/contact management
- Handles API responses and error cases

## Security

- API credentials are stored securely using keyring
- No hardcoded credentials in the codebase
- Secure API communication with proper error handling

## Development

To extend the functionality:
1. Add new tools to the `hubspot_tool.py`
2. Register them in the MCP server
3. Update the LangChain agent's prompt template as needed

## Error Handling

The application includes comprehensive error handling for:
- API communication issues
- Invalid data formats
- Authentication errors
- Server connection problems

## Contributing

Feel free to submit issues and enhancement requests! 