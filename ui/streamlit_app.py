import streamlit as st
import os
import json
import yaml
import sys
import traceback

st.set_page_config(page_title="AI Test Suite v2 (Red Team Max)", layout="wide")
st.title("🛡️ AI Test Suite v2 (Red Team Max)")

st.write("DEBUG: App launched")

# Ensure all folders exist
for folder in ["scenarios", "plugins", "reports"]:
    st.write(f"DEBUG: Checking folder {folder}")
    if not os.path.exists(folder):
        try:
            os.makedirs(folder, exist_ok=True)
            st.write(f"DEBUG: Created folder {folder}")
        except Exception as e:
            st.error(f"Required folder '{folder}' could not be created: {e}")
            st.text(traceback.format_exc())

st.write("DEBUG: Starting imports")
try:
    from core.api_client import APIClient, load_config
    from core.plugin_loader import discover_plugins
    from core.scenario_loader import load_scenarios
    from core.reporting import generate_report, save_html
    st.write("DEBUG: Core modules imported")
except Exception as e:
    st.error(f"Import error: {e}")
    st.text(traceback.format_exc())

# Config load
try:
    st.write("DEBUG: Loading config")
    config = load_config()
    st.write(f"DEBUG: Config loaded: {config}")
except Exception as e:
    st.error(f"Error loading config: {e}")
    st.text(traceback.format_exc())
    config = {}

# Mode and API
try:
    st.write("DEBUG: Sidebar mode select")
    mode = st.sidebar.radio("Mode", ["demo", "live"], index=0)
    config["mode"] = mode
    st.write(f"DEBUG: Mode set to {mode}")
except Exception as e:
    st.error(f"Sidebar mode error: {e}")
    st.text(traceback.format_exc())
    mode = "demo"
    config["mode"] = mode

try:
    st.write("DEBUG: Sidebar endpoint select")
    endpoint = st.sidebar.text_input("LLM Endpoint/Model", config.get("api_endpoint", ""))
    if endpoint:
        config["api_endpoint"] = endpoint
    st.write(f"DEBUG: Endpoint: {endpoint}")
except Exception as e:
    st.error(f"Sidebar endpoint error: {e}")
    st.text(traceback.format_exc())

try:
    st.write("DEBUG: Initializing APIClient")
    api_client = APIClient(config)
    st.write("DEBUG: APIClient created")
except Exception as e:
    st.error(f"APIClient init error: {e}")
    st.text(traceback.format_exc())
    api_client = None

try:
    st.write("DEBUG: Discovering plugins")
    plugins = discover_plugins()
    st.write(f"DEBUG: Plugins discovered: {len(plugins)}")
except Exception as e:
    st.error(f"Plug-in discovery error: {e}")
    st.text(traceback.format_exc())
    plugins = []
if not plugins:
    st.warning("No plug-ins found! Check your /plugins/ directory and plug-in format.")

# Scenario source
try:
    st.write("DEBUG: Scenario source radio")
    scenario_source = st.radio("Test Source", ["Prebuilt", "Manual"])
    st.write(f"DEBUG: Scenario source: {scenario_source}")
except Exception as e:
    st.error(f"Scenario source selector error: {e}")
    st.text(traceback.format_exc())
    scenario_source = "Prebuilt"

if scenario_source == "Prebuilt":
    try:
        st.write("DEBUG: Listing scenario files")
        scenario_files = [f for f in os.listdir("scenarios") if f.endswith(".json")]
        st.write(f"DEBUG: Scenario files: {scenario_files}")
        if not scenario_files:
            st.error("No scenario files found in /scenarios/")
        else:
            file = st.selectbox("Scenario file", scenario_files)
            st.write(f"DEBUG: Selected scenario file: {file}")
            if st.button("Load Scenarios"):
                st.write("DEBUG: Load Scenarios button c
