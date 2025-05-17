from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.schema.messages import AIMessage, HumanMessage
from langchain_mcp_tool import MCPTool

def create_mcp_agent():
    """Create a LangChain agent with Ollama LLM and MCP tool."""
    
    # Initialize Ollama with llama2 model
    llm = Ollama(model="llama2")
    
    # Initialize our MCP tool
    tools = [MCPTool()]
    
    # Convert tools to OpenAI functions format
    functions = [format_tool_to_openai_function(t) for t in tools]
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI assistant that can interact with HubSpot through MCP tools.
        When creating or updating leads, make sure to validate the data format before sending.
        Always provide clear explanations of what you're doing."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor

if __name__ == "__main__":
    # Create the agent
    agent = create_mcp_agent()
    
    # Example interaction
    result = agent.invoke({
        "input": "Create a new lead for John Smith with email john.smith@example.com"
    })
    
    print("\nAgent Response:")
    print(result["output"]) 