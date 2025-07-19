import sys
import os
import streamlit as st
import json

# Fix sys.path so 'core', 'plugins', etc are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.plugin_loader import load_plugins
from core.scenario_loader import load_scenarios
from core.reporting import generate_json_report
from core.generate_report import create_pdf_report

# App title and style
st.set_page_config(page_title="AI Test Suite v2 (Red Team Max)", layout="wide")
st.markdown("# 🛡️ AI Test Suite v2 (Red Team Max)")

# Sidebar: Demo/Live toggle
st.sidebar.title("⚡ Test Execution Mode")
mode = st.sidebar.radio("Choose mode:", ["Demo (offline/mock)", "Live (real API)"])
endpoint = st.sidebar.text_input("LLM Endpoint/Model", "https://api.openai.com/v1/chat/completions" if mode == "Live (real API)" else "")

# Load plugins and scenarios
with st.spinner("Loading plugins and scenarios..."):
    plugins = load_plugins()
    plugin_names = sorted([p["name"] for p in plugins])
    scenarios = load_scenarios()
    scenario_files = sorted(list(scenarios.keys()))

# Main UI: Load Scenarios (dropdown + drag-drop)
st.markdown("## 🧪 Load Test Scenarios")
preset_selected = st.multiselect("Select scenario(s) from built-in library:", options=scenario_files)

uploaded = st.file_uploader(
    "Or upload custom scenario JSON(s)", type="json", accept_multiple_files=True,
    help="Upload your own malformed or custom scenario files"
)
user_scenarios = []
if uploaded:
    for f in uploaded:
        try:
            js = json.load(f)
            user_scenarios.append({"filename": f.name, "data": js})
            st.success(f"Loaded scenario: {f.name}")
        except Exception as e:
            st.error(f"Failed to load {f.name}: {e}")

# Scenario collection
selected_scenarios = []
if preset_selected:
    for fname in preset_selected:
        selected_scenarios.append({"filename": fname, "data": scenarios[fname]})
if user_scenarios:
    selected_scenarios.extend(user_scenarios)

if not selected_scenarios:
    st.info("No scenarios loaded yet. Choose from library or upload custom JSON.")
else:
    st.success(f"Loaded {len(selected_scenarios)} scenario(s) for testing.")

# Plugin selection
st.markdown("## 🧰 Select Attack/Testing Plugins")
selected_plugins = st.multiselect(
    "Select plugins/tools to run:", options=plugin_names, default=plugin_names,
    help="All are selected by default. Unselect to exclude some."
)

if not selected_plugins:
    st.warning("Please select at least one plugin.")
    st.stop()

# Run button (enabled only if at least one scenario and one plugin)
run_all = st.button("🚀 RUN TESTS on SELECTED SCENARIOS/PLUGINS", disabled=not(selected_scenarios and selected_plugins))

# Session state: Results
if "results" not in st.session_state:
    st.session_state["results"] = []

# Test execution
if run_all:
    with st.spinner("Running all selected plugins on all scenarios..."):
        results = []
        for scenario in selected_scenarios:
            s_name = scenario["filename"]
            s_data = scenario["data"]
            for plugin in plugins:
                if plugin["name"] in selected_plugins:
                    try:
                        outcome = plugin["run"](s_data, endpoint, mode)
                        results.append({
                            "scenario": s_name,
                            "plugin": plugin["name"],
                            "result": outcome
                        })
                    except Exception as e:
                        results.append({
                            "scenario": s_name,
                            "plugin": plugin["name"],
                            "result": {"error": str(e)}
                        })
        st.session_state["results"] = results
    st.success("All tests complete!")

# Reporting section
if st.session_state["results"]:
    st.markdown("## 📊 View/Export Report")
    report_data = st.session_state["results"]

    # Download JSON
    st.download_button(
        "Download JSON Report",
        data=json.dumps(report_data, indent=2),
        file_name="ai_test_report.json",
        mime="application/json"
    )

    # Download PDF
    pdf_bytes = create_pdf_report(report_data)
    st.download_button(
        "Download PDF Report",
        data=pdf_bytes,
        file_name="ai_test_report.pdf",
        mime="application/pdf"
    )

    # Show table
    st.dataframe(report_data)

