import requests
import datetime
from typing import Dict, List, Any

# LangChain imports
from langchain.agents import AgentExecutor, create_openai_tools_agent, Tool
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage

# Constants
MCP_SERVER_URL = "http://127.0.0.1:8000"  # Default to localhost MCP server

def fetch_tools_from_mcp() -> List[Dict[str, Any]]:
    """Fetch available tools from the MCP server."""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/mcp/tools")
        response.raise_for_status()
        tools_data = response.json()
        return tools_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tools from MCP server: {e}")
        return []

def run_tool_on_mcp(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Run a specific tool on the MCP server."""
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/{tool_name}",
            json=tool_input
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error running tool '{tool_name}': {e}"

def create_mcp_agent() -> AgentExecutor:
    """Create a LangChain agent that interacts with MCP tools."""
    
    # Initialize tools
    tools = fetch_tools_from_mcp()

    # for testing purposes, only use the create_lead tool
    tools = [
        Tool(
            name="create_lead",
            func=lambda x: run_tool_on_mcp("create_lead", x),
            description="Create a new lead in HubSpot with the provided information. Expects a JSON payload with lead properties."
        )
    ]

    # Create the system message template
    system_template = """You are a HubSpot lead creation assistant. Your primary task is to create leads in HubSpot.

You have access to the following tools:
{tools}

Your task has three parts:

1. **Eligibility Check**: Read the email content and decide whether it should be considered a potential CRM lead. Eligible emails typically express interest in products/services, request more information, or mention purchasing intent.

2. **Information Extraction**: If eligible, extract the following fields from the email:
- First name and last name (extracted from the full name)
- Email address
- Company name
- Job title
- Phone number
- Interest
- Notes
- Creation timestamp

3. **Lead Creation**: Use the create_lead tool with the extracted information.

Example tool usage:
create_lead(
    lead={{
        "properties": {{
            "name": "John Doe",
            "email": "john@example.com",
            "company": "Acme Corp",
            "job_title": "CTO",
            "phone": "+1-555-123-4567",
            "interest": "cloud infrastructure",
            "notes": "Interested in enterprise pricing and onboarding within 30 days."
        }}
    }}
)

Remember to:
1. Always validate the data before creating a lead
2. Include all required fields
3. Format dates in ISO format (YYYY-MM-DDTHH:MM:SSZ)
4. Provide clear explanations of your actions"""
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Initialize Ollama with llama2 model
    llm = Ollama(model="llama2")

    # Create the agent
    agent = create_openai_tools_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # Create and return the agent executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )

if __name__ == "__main__":
    # Create the agent
    agent = create_mcp_agent()

    print(agent.tools)
    tools_from_mcp = agent.tools
    if len(tools_from_mcp) == 0:
        print("No tools found")
        exit()
    
    # Example interaction with current timestamp
    current_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    test_email = f"""
    From: John Smith <john.smith@acme.com>
    Subject: Enterprise Solution Inquiry
    
    Hi,
    
    I'm John Smith, CTO at Acme Corporation. We're looking to implement a cloud infrastructure solution for our growing team of 200+ developers.
    
    Could you provide information about your enterprise pricing and implementation timeline? We're hoping to start within the next 30 days.
    
    You can reach me at +1-555-0123 for any questions.
    
    Best regards,
    John
    
    Timestamp: {current_time}
    """
    
    # Process the test email
    result = agent.invoke({
        "input": f"Process this email for lead creation: {test_email}",
        "agent_scratchpad": [],  # Initialize empty scratchpad
        "tools": tools_from_mcp
    })
    
    print("\nAgent Response:")
    print(result["output"]) 