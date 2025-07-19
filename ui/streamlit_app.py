import streamlit as st
import json
import os
from core.plugin_loader import load_plugins
from core.scenario_loader import load_scenarios
from core.reporting import generate_json_report
from core.generate_report import create_pdf_report

st.set_page_config(
    page_title="AI Test Suite v2 (Red Team Max)",
    page_icon=":shield:",
    layout="wide"
)

# --- DEMO / LIVE Toggle ---
st.sidebar.title("⚡ Test Execution Mode")
mode = st.sidebar.radio("Choose mode:", ["Demo (offline/mock)", "Live (real API)"])
st.session_state['mode'] = 'demo' if mode.startswith("Demo") else 'live'
st.sidebar.text_input("LLM Endpoint/Model", key="llm_endpoint", value="https://api.openai.com/v1/chat/completions")

# --- Load Scenarios ---
st.markdown("# 🧪 Load Test Scenarios")

scenario_folder = os.path.join(os.path.dirname(__file__), "../scenarios")
available_scenarios = [f for f in os.listdir(scenario_folder) if f.endswith(".json")]
scenario_choice = st.selectbox("Select scenario(s) from built-in library:", ["Choose options"] + available_scenarios, key="scenario_choice")
uploaded_files = st.file_uploader("Or upload custom scenario JSON(s)", accept_multiple_files=True, type=["json"])

scenario_data = []
if scenario_choice and scenario_choice != "Choose options":
    path = os.path.join(scenario_folder, scenario_choice)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        scenario_data.append({"name": scenario_choice, "content": data})
if uploaded_files:
    for up in uploaded_files:
        data = json.load(up)
        scenario_data.append({"name": up.name, "content": data})

if not scenario_data:
    st.info("No valid scenarios loaded yet.")
else:
    st.success(f"Loaded {len(scenario_data)} scenario(s) for testing.")

# --- Plugin Loader ---
st.markdown("## 🧰 Select Attack/Testing Plugins")
plugins = load_plugins()
plugin_names = list(plugins.keys())
default_plugins = plugin_names

selected_plugins = st.multiselect(
    "Select plugins/tools to run (all by default):",
    plugin_names,
    default=default_plugins,
    key="selected_plugins"
)

if not selected_plugins:
    st.warning("Please select at least one plugin to run.")

# --- Run Button ---
if st.button("🚀 Run selected test(s) on selected scenario(s)"):
    if not scenario_data or not selected_plugins:
        st.error("You must load at least one scenario and select one plugin.")
    else:
        results = []
        for scenario in scenario_data:
            for plugin_name in selected_plugins:
                plugin = plugins[plugin_name]
                try:
                    output = plugin.run(scenario["content"], mode=st.session_state['mode'])
                    results.append({
                        "scenario": scenario["name"],
                        "plugin": plugin_name,
                        "result": output
                    })
                except Exception as e:
                    results.append({
                        "scenario": scenario["name"],
                        "plugin": plugin_name,
                        "result": f"Error: {e}"
                    })
        st.session_state["results"] = results
        st.success("All tests complete!")

# --- Reporting & Export ---
if "results" in st.session_state and st.session_state["results"]:
    st.header("📊 View/Export Report")
    # JSON Report
    st.download_button(
        "⬇️ Download JSON Report",
        data=json.dumps(st.session_state["results"], indent=2),
        file_name="results.json",
        mime="application/json"
    )
    # PDF Report
    pdf_buf = create_pdf_report(st.session_state["results"])
    st.download_button(
        "⬇️ Download PDF Report",
        data=pdf_buf,
        file_name="AI_Test_Report.pdf",
        mime="application/pdf"
    )
    # Show some quick result stats if you like
    st.write("### Test Results Overview")
    st.json(st.session_state["results"])

st.markdown("---")
st.caption("AI Test Suite v2 by AK-LLM | Red Team Max Edition")

