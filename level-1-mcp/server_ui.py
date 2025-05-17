import streamlit as st
import time
from fastmcp import FastMCP
from hubspot.hubspot_tool import create_lead as create_hubspot_lead
from fastapi import FastAPI

# --- Streamlit UI ---
class MCPStreamlitUI:
    def __init__(self):
        st.set_page_config(layout="wide")
        st.title("MCP FastAPI Server Control Panel")
        if 'server_instance' not in st.session_state:
            st.session_state.server_instance = None

    def _get_server_instance(self) -> FastMCP | None:
        return st.session_state.get('server_instance')

    def _is_server_running(self) -> bool:
        server = self._get_server_instance()
        return server is not None

    def _initialize_mcp(self) -> FastMCP:
        # Create MCP instance directly
        mcp = FastMCP(
            name="HubSpot MCP",
            description="Tool to create a HubSpot lead"
        )
        
        # Register the tool using the tool decorator
        @mcp.tool()
        async def create_lead(lead: dict) -> int:
            st.progress("initializing create_lead tool")
            return create_hubspot_lead(lead)
        
        # Debug: Print registered tools
        st.write("Debug - Registered tools:", mcp.get_tools())
        return mcp

    def display_controls(self):
        # Server control buttons
        col1, col2, col3 = st.columns([1, 1, 2])

        server_instance = self._get_server_instance()
        is_server_actually_running = self._is_server_running()

        with col1:
            if st.button("🚀 Start Server", disabled=is_server_actually_running, type="primary", use_container_width=True):
                if server_instance is None:
                    mcp = self._initialize_mcp()
                    st.session_state.server_instance = mcp
                    st.success("Server instance initialized.")
                    server_instance = st.session_state.server_instance # refresh local var
                
                if server_instance:
                    try:
                        with st.spinner("Starting server..."):
                            # Start the server in a background thread
                            import threading
                            def run_server():
                                server_instance.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
                            
                            thread = threading.Thread(target=run_server, daemon=True)
                            thread.start()
                            st.success("Server started successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error starting server: {e}")
                else:
                    st.error("Server instance could not be initialized.")

        with col2:
            if st.button("🛑 Stop Server", disabled=not is_server_actually_running, use_container_width=True):
                if server_instance:
                    try:
                        with st.spinner("Stopping server..."):
                            # The server will be stopped when the thread is terminated
                            st.session_state.server_instance = None
                        st.info("Server stop signal sent. It may take a few moments to fully shut down.")
                        time.sleep(1) # Give a moment for the server to actually stop
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error stopping server: {e}")
                else:
                    st.warning("No server instance to stop.")

        with col3:
            status_text = "Running" if is_server_actually_running else "Stopped"
            status_color = "green" if is_server_actually_running else "red"
            st.markdown(f"**Server Status:** <span style='color:{status_color}; font-weight:bold;'>{status_text}</span>", unsafe_allow_html=True)
            if is_server_actually_running:
                api_url = "http://127.0.0.1:8000"
                st.markdown(f"Serving on: `{api_url}`")
                st.markdown(f"API Docs: `{api_url}/docs`")

    async def get_tools(server_instance):
        return await server_instance.get_tools()

    def display_tool_info(self):
        server_instance = self._get_server_instance()
        if server_instance:
            st.subheader("Registered Tools")
            
            # Debug information
            st.write("Debug - Server instance:", server_instance)
            # st.write("Debug - Server instance type:", type(server_instance))
            
            # Get tools using the get_tools method
            import asyncio
            try:
                # Create a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Get tools synchronously
                tools = loop.run_until_complete(server_instance.get_tools())
                st.write("Debug - Tools from get_tools():", tools)
                
                if tools:
                    for tool_name in tools.keys():
                        st.markdown(f"- `{tool_name}`")
                else:
                    st.markdown("No tools registered.")
                    
                # Close the loop
                loop.close()
            except Exception as e:
                st.error(f"Error getting tools: {str(e)}")
                st.markdown("No tools registered.")

    def render(self):
        self.display_controls()
        st.divider()
        self.display_tool_info()

def main_streamlit_ui():
    ui = MCPStreamlitUI()
    ui.render()

if __name__ == "__main__":
    main_streamlit_ui()