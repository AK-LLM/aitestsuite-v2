import os
import sys
import json
import streamlit as st
import importlib
from glob import glob

# --- Fix Import Path for core and plugins (runs from project root) ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.plugin_loader import load_plugins
from core.reporting import generate_report_json, generate_report_pdf

SCENARIO_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'scenarios')

st.set_page_config(page_title="AI Test Suite v2 (Red Team Max)", layout="wide")
st.title("🛡️ AI Test Suite v2 (Red Team Max)")

# --- Mode selection ---
mode = st.sidebar.radio("Choose mode:", ["Demo (offline/mock)", "Live (real API)"])
st.sidebar.write("LLM Endpoint/Model")
if mode == "Live (real API)":
    endpoint = st.sidebar.text_input("LLM Endpoint URL", value="https://api.openai.com/v1/chat/completions")
    api_key = st.sidebar.text_input("API Key", type="password")
else:
    endpoint = None
    api_key = None

# --- Load built-in scenarios for dropdown ---
def get_built_in_scenarios():
    if not os.path.exists(SCENARIO_FOLDER):
        return []
    json_files = glob(os.path.join(SCENARIO_FOLDER, "*.json"))
    scenario_names = [os.path.basename(f) for f in json_files]
    return scenario_names

st.subheader("🧪 Load Test Scenarios")
scenario_list = get_built_in_scenarios()
selected_scenarios = st.multiselect("Select scenario(s) from built-in library:", scenario_list)
uploaded_files = st.file_uploader("Or upload custom scenario JSON(s)", type="json", accept_multiple_files=True)

# --- Load scenario data ---
scenario_data = []
for scen in selected_scenarios:
    with open(os.path.join(SCENARIO_FOLDER, scen), "r", encoding="utf-8") as f:
        scenario_data.append(json.load(f))
for uploaded in uploaded_files or []:
    scenario_data.append(json.load(uploaded))

if not scenario_data:
    st.info("No valid scenarios loaded yet.")

# --- Plugins ---
st.subheader("💼 Select Attack/Testing Plugins")
plugins = load_plugins()
plugin_names = list(plugins.keys())
selected_plugins = st.multiselect(
    "Select plugins/tools to run:",
    plugin_names,
    default=plugin_names
)

if not selected_plugins:
    st.warning("Please select at least one plugin to run.")

# --- Main Test Button ---
run_tests = st.button("🚀 Run selected TESTS/ATTACKS on loaded SCENARIOS")
test_results = []

if run_tests and scenario_data and selected_plugins:
    for scenario in scenario_data:
        result = {}
        for plugin_name in selected_plugins:
            plugin = plugins[plugin_name]
            # Each plugin is assumed to have a .run(scenario) method
            try:
                result[plugin_name] = plugin.run(scenario, mode=mode, endpoint=endpoint, api_key=api_key)
            except Exception as e:
                result[plugin_name] = {"error": str(e)}
        test_results.append({
            "scenario": scenario,
            "results": result
        })
    st.success("All tests complete!")

    # --- Save to session state for reporting ---
    st.session_state["results"] = test_results

# --- Report Section ---
st.subheader("📊 View/Export Report")

if "results" in st.session_state:
    # JSON Report
    st.download_button(
        label="⬇️ Download JSON Report",
        data=json.dumps(st.session_state["results"], indent=2),
        file_name="ai_test_suite_report.json",
        mime="application/json"
    )
    # PDF Report
    pdf_bytes = generate_report_pdf(st.session_state["results"])
    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_bytes,
        file_name="ai_test_suite_report.pdf",
        mime="application/pdf"
    )

# --- Helper Functions (core/reporting.py should have these) ---
# generate_report_json(results): returns JSON serializable dict
# generate_report_pdf(results): returns PDF as bytes

