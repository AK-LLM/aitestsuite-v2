import streamlit as st
import os
import sys
import json

# --- ENSURE ROOT PATH ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.plugin_loader import discover_plugins
from core.reporting import generate_report  # Make sure generate_report exists and does PDF/JSON
from core.scenario_loader import load_scenarios

st.set_page_config(page_title="AI Test Suite v2 (Red Team Max)", layout="wide")

st.title("🛡️ AI Test Suite v2 (Red Team Max)")

# --- MODE TOGGLE ---
mode = st.sidebar.radio("Choose mode:", ["Demo (offline/mock)", "Live (real API)"], index=0)
llm_endpoint = st.sidebar.text_input("LLM Endpoint/Model", "https://api.openai.com/v1/chat/completions" if mode == "Live (real API)" else "")

# --- Load Scenarios ---
scenario_dir = os.path.join(os.path.dirname(__file__), '..', 'scenarios')
preset_files = [f for f in os.listdir(scenario_dir) if f.endswith('.json')]
preset_files.sort()

preset_choice = st.selectbox("Select scenario(s) from built-in library:", ["Choose options"] + preset_files)
uploaded_files = st.file_uploader("Or upload custom scenario JSON(s)", type="json", accept_multiple_files=True)

loaded_scenarios = []
if preset_choice and preset_choice != "Choose options":
    with open(os.path.join(scenario_dir, preset_choice), 'r', encoding='utf-8') as f:
        loaded_scenarios.append(json.load(f))

if uploaded_files:
    for up in uploaded_files:
        loaded_scenarios.append(json.load(up))

if not loaded_scenarios:
    st.info("Please select or upload at least one test scenario.")
    st.stop()

# --- Load Plugins ---
plugins = discover_plugins()
plugin_names = [p["name"] for p in plugins]
selected_plugins = st.multiselect(
    "Select plugins/tools to run (all by default):", plugin_names, default=plugin_names
)

if not selected_plugins:
    st.warning("Please select at least one plugin to run.")
    st.stop()

if st.button("🚀 Run Selected Plugins on Selected Scenarios"):
    all_results = []
    with st.spinner("Running selected plugins on scenarios..."):
        for scenario in loaded_scenarios:
            for plugin in plugins:
                if plugin["name"] in selected_plugins:
                    try:
                        result = plugin["module"].run(scenario)
                        all_results.append({
                            "plugin": plugin["name"],
                            "scenario": scenario.get("name", "Unnamed"),
                            "result": result
                        })
                    except Exception as e:
                        all_results.append({
                            "plugin": plugin["name"],
                            "scenario": scenario.get("name", "Unnamed"),
                            "result": f"ERROR: {e}"
                        })
    st.success("All tests complete!")
    st.session_state["test_results"] = all_results

# --- REPORTING ---
if "test_results" in st.session_state and st.session_state["test_results"]:
    st.header("📊 View/Export Report")
    if st.button("Download JSON Report"):
        st.download_button(
            "Download JSON Report",
            data=json.dumps(st.session_state["test_results"], indent=2),
            file_name="test_results.json"
        )
    if st.button("Download PDF Report"):
        pdf_bytes = generate_report(st.session_state["test_results"])  # Should return BytesIO or bytes
        st.download_button(
            "Download PDF Report",
            data=pdf_bytes,
            file_name="test_results.pdf"
        )
