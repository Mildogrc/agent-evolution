from typing import Any, Dict, Optional
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
import requests
import json

class MCPInput(BaseModel):
    """Input for the MCP tool."""
    tool_name: str = Field(..., description="The name of the MCP tool to call")
    parameters: Dict[str, Any] = Field(..., description="The parameters to pass to the MCP tool")

class MCPTool(BaseTool):
    """Tool for interacting with MCP endpoints."""
    name = "mcp_tool"
    description = """Use this tool to interact with MCP endpoints. 
    You need to provide the tool name and parameters.
    For example, to create a lead you would use:
    {
        "tool_name": "create_lead",
        "parameters": {
            "lead": {
                "properties": {
                    "email": "example@email.com",
                    "firstname": "John",
                    "lastname": "Doe"
                }
            }
        }
    }
    """
    args_schema = MCPInput

    def _run(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute the tool."""
        base_url = "http://127.0.0.1:8000"
        endpoint = f"{base_url}/mcp/tools/{tool_name}"
        
        try:
            response = requests.post(
                endpoint,
                json=parameters,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling MCP endpoint: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus Code: {e.response.status_code}"
                error_msg += f"\nResponse Body: {e.response.text}"
            return {"error": error_msg}

    async def _arun(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute the tool asynchronously."""
        # For now, we'll just call the sync version
        # In a production environment, you'd want to use aiohttp or httpx for async requests
        return self._run(tool_name, parameters)

# Example usage:
if __name__ == "__main__":
    # Create an instance of the tool
    mcp_tool = MCPTool()
    
    # Example: Create a lead
    result = mcp_tool.run({
        "tool_name": "create_lead",
        "parameters": {
            "lead": {
                "properties": {
                    "email": "test@example.com",
                    "firstname": "John",
                    "lastname": "Doe"
                }
            }
        }
    })
    print("Result:", json.dumps(result, indent=2)) 