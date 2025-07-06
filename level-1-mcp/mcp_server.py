import threading
import time
from fastmcp import FastMCP as Server
from hubspot.hubspot_tool import create_lead as create_hubspot_lead

class FastMCPServerWrapper:
    def __init__(self):
        self.mcp_instance: Server | None = None
        self._server_thread: threading.Thread | None = None
        self._server_running_event = threading.Event()

    def initialize_server(self):
        """Creates and configures the Server instance and registers tools."""
        if self.mcp_instance is None:
            server_obj = Server( 
                name="HubSpot MCP"
            )
            
            async def create_lead(lead: dict) -> int:
                print("FastMCPServerWrapper: initializing create_lead tool")
                return create_hubspot_lead(lead)
            
            try:
                server_obj.add_tool(create_lead, name="create_lead")
                print(f"Debug - Registered tools in wrapper (after add_tool): {server_obj.get_tools()}") 
            except AttributeError:
                print("Error: server_obj does not have an attribute 'add_tool'. Tool registration failed.")
            except Exception as e:
                print(f"Error during server_obj.add_tool: {e}. Tool registration failed.")

            self.mcp_instance = server_obj
            return True
        return False

    def start_server(self, host="127.0.0.1", port=8000, path="/mcp"):
        """Starts the Server instance in a background thread."""
        if not self.mcp_instance:
            print("MCP instance not initialized. Initializing now...")
            self.initialize_server()

        if self.mcp_instance and not self.is_running():
            def run():
                try:
                    self._server_running_event.set()
                    print(f"FastMCPServerWrapper: Starting server on {host}:{port}{path}")
                    self.mcp_instance.run(transport="streamable-http", host=host, port=port, path=path) 
                except Exception as e:
                    print(f"FastMCPServerWrapper: Error running server: {e}")
                finally:
                    self._server_running_event.clear()
                    print("FastMCPServerWrapper: Server stopped.")

            self._server_thread = threading.Thread(target=run, daemon=True)
            self._server_thread.start()
            time.sleep(0.1)
            return True
        elif self.is_running():
            print("FastMCPServerWrapper: Server is already running.")
            return False
        else:
            print("FastMCPServerWrapper: Could not start server, mcp_instance is None even after trying to initialize.")
            return False

    def stop_server(self):
        """Stops the Server instance."""
        if self.is_running() and self.mcp_instance:
            print("FastMCPServerWrapper: Sending stop signal to server...")
            self._server_running_event.clear() 
            self.
            print("FastMCPServerWrapper: Stop signal processed. Actual stop depends on Server behavior and app lifecycle.")
            return True
        print("FastMCPServerWrapper: Server is not running or no instance to stop.")
        return False

    def is_running(self) -> bool:
        """Checks if the server is considered active."""
        return self._server_running_event.is_set() and self._server_thread is not None and self._server_thread.is_alive()

    def get_mcp_instance(self) -> Server | None:
        """Returns the underlying Server instance."""
        return self.mcp_instance
