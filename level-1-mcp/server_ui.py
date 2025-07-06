import streamlit as st
import time
from mcp_server import FastMCPServerWrapper # Added
import asyncio # Keep for display_tool_info

# --- Streamlit UI ---
class MCPStreamlitUI:
    def __init__(self):
        st.set_page_config(layout="wide")
        st.title("MCP FastAPI Server Control Panel")
        if 'mcp_server_wrapper' not in st.session_state: # Changed
            st.session_state.mcp_server_wrapper = None

    def _get_server_wrapper_instance(self) -> FastMCPServerWrapper | None: # Renamed and type hint updated
        return st.session_state.get('mcp_server_wrapper')

    def _is_server_running(self) -> bool:
        wrapper = self._get_server_wrapper_instance()
        return wrapper.is_running() if wrapper else False

    def display_controls(self):
        col1, col2, col3 = st.columns([1, 1, 2])

        is_server_actually_running = self._is_server_running() 

        with col1:
            if st.button("🚀 Start Server", disabled=is_server_actually_running, type="primary", use_container_width=True):
                current_wrapper = self._get_server_wrapper_instance() 
                if current_wrapper is None:
                    current_wrapper = FastMCPServerWrapper()
                    st.session_state.mcp_server_wrapper = current_wrapper
                    st.info("Server wrapper initialized.") 
                
                if current_wrapper:
                    try:
                        with st.spinner("Starting server..."):
                            # The wrapper's start_server method now handles initialization if needed.
                            if current_wrapper.start_server():
                                st.success("Server start command issued successfully!")
                                st.rerun()
                            else:
                                # This case could mean it was already running or failed to initialize and start.
                                # The is_running() check should ideally prevent starting if already running.
                                # The wrapper's start_server prints messages, so UI can be minimal here.
                                st.warning("Server might be already running or failed to start. Check console/logs.")
                                st.rerun() # Rerun to update status, if it did start despite warning
                    except Exception as e:
                        st.error(f"Error during server start sequence: {e}")
                else:
                    st.error("Server wrapper could not be accessed or initialized.") # Should not happen if logic above is correct

        with col2:
            if st.button("🛑 Stop Server", disabled=not is_server_actually_running, use_container_width=True):
                wrapper_to_stop = self._get_server_wrapper_instance()
                if wrapper_to_stop and wrapper_to_stop.is_running():
                    try:
                        with st.spinner("Stopping server..."):
                            if wrapper_to_stop.stop_server():
                                st.info("Server stop signal sent. It may take a few moments to fully shut down.")
                            else:
                                st.warning("Server stop signal failed or server was already stopped.")
                        time.sleep(1) 
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error stopping server: {e}")
                else:
                    st.warning("No server running to stop, or wrapper not found.")

        with col3:
            # Use self._is_server_running() for the most up-to-date status
            current_status_running = self._is_server_running()
            status_text = "Running" if current_status_running else "Stopped"
            status_color = "green" if current_status_running else "red"
            st.markdown(f"**Server Status:** <span style='color:{status_color}; font-weight:bold;'>{status_text}</span>", unsafe_allow_html=True)
            if current_status_running:
                api_url = "http://127.0.0.1:8000" # TODO: Make this dynamic if port/host can change
                st.markdown(f"Serving on: `{api_url}`")
                st.markdown(f"API Docs: `{api_url}/docs`")

    def display_tool_info(self):
        wrapper = self._get_server_wrapper_instance()
        if wrapper and wrapper.is_running(): # Also check if server is running
            mcp_instance = wrapper.get_mcp_instance()
            if mcp_instance:
                st.subheader("Registered Tools")
                # st.write("Debug - MCP instance from wrapper:", mcp_instance) # Optional debug line
                
                try:
                    # Ensure an event loop exists for this thread if not main, or if previous closed.
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_closed():
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                    except RuntimeError: # No current event loop
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    tools = loop.run_until_complete(mcp_instance.get_tools())
                    # st.write("Debug - Tools from get_tools():", tools) # Optional debug line
                    
                    if tools:
                        for tool_name in tools.keys():
                            st.markdown(f"- `{tool_name}`")
                    else:
                        st.markdown("No tools registered on the MCP instance.")
                    # Consider not closing the loop here if other async operations might occur in Streamlit context
                    # loop.close() 
                except Exception as e:
                    st.error(f"Error getting tools: {str(e)}")
            else:
                st.markdown("MCP instance not available from wrapper (server might be stopping or failed).")
        elif wrapper and not wrapper.is_running():
            st.markdown("Server is not currently running. Start the server to see tool info.")
        else:
            st.markdown("Server wrapper not initialized. Start the server to see tool info.")
            
    def render(self):
        self.display_controls()
        st.divider()
        self.display_tool_info()

def main_streamlit_ui():
    ui = MCPStreamlitUI()
    ui.render()

if __name__ == "__main__":
    main_streamlit_ui()