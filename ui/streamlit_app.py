import streamlit as st
import os
import json
import importlib.util
import pandas as pd
from core.generate_report import create_pdf_report

SCENARIO_FOLDER = "scenarios"
PLUGIN_FOLDER = "plugins"

st.set_page_config(page_title="AI Test Suite v2 (Red Team Max)", layout="wide")
st.markdown("# 🛡️ AI Test Suite v2 (Red Team Max)")

# === 1. SCENARIO LOADER ===
preset_scenarios = [
    f for f in os.listdir(SCENARIO_FOLDER)
    if f.endswith(".json")
]
all_scenarios = []
for scenario_file in preset_scenarios:
    with open(os.path.join(SCENARIO_FOLDER, scenario_file), "r", encoding="utf-8") as f:
        loaded = json.load(f)
        if isinstance(loaded, list):
            all_scenarios += loaded
        else:
            all_scenarios.append(loaded)
scenario_names = [s.get("scenario_id", f"Scenario {i+1}") for i, s in enumerate(all_scenarios)]

# === 2. PLUGIN LOADER ===
def load_plugins(plugin_folder):
    plugins = {}
    for fname in os.listdir(plugin_folder):
        if fname.endswith(".py") and fname != "__init__.py":
            plugin_name = fname[:-3]
            module_path = os.path.join(plugin_folder, fname)
            spec = importlib.util.spec_from_file_location(plugin_name, module_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)
                    plugins[plugin_name] = mod
                except Exception:
                    pass
    return plugins

plugins = load_plugins(PLUGIN_FOLDER)
plugin_list = sorted(list(plugins.keys()))

# === 3. SIDEBAR: MODE TOGGLE ===
st.sidebar.header("Test Mode & Selection")
mode = st.sidebar.radio("Mode", ["Demo/Offline", "Live/API"])

api_endpoint = ""
api_key = ""
if mode == "Live/API":
    api_endpoint = st.sidebar.text_input("API Endpoint URL", value="", help="Paste your LLM endpoint")
    api_key = st.sidebar.text_input("API Key", value="", type="password", help="Paste your API key")

selected_scenarios_idx = st.sidebar.multiselect(
    "Select Scenarios", options=list(range(len(scenario_names))),
    format_func=lambda idx: scenario_names[idx], default=list(range(len(scenario_names)))
)
selected_plugins = st.sidebar.multiselect(
    "Select Plugins", plugin_list, default=plugin_list
)

# === 4. RUN BUTTONS ===
col1, col2 = st.columns(2)
run_selected = col1.button("▶️ Run Selected")
run_all = col2.button("🚀 RUN ALL TESTS")

# === 5. RUN TESTS ===
def run_tests(plugins_to_run, scenarios_to_run, mode, api_endpoint="", api_key=""):
    results = []
    for sidx in scenarios_to_run:
        scenario = all_scenarios[sidx]
        result_obj = {"scenario": scenario, "results": []}
        for plugin_name in plugins_to_run:
            plugin = plugins[plugin_name]
            try:
                if mode == "Live/API":
                    res = plugin.run_api(scenario, api_endpoint, api_key)
                else:
                    res = plugin.run(scenario)
                result_obj["results"].append({"plugin": plugin_name, "result": res})
            except Exception as e:
                result_obj["results"].append({"plugin": plugin_name, "result": {
                    "risk_level": "Unknown", "issue": f"Plugin error: {e}", "recommendation": "Check plugin"
                }})
        results.append(result_obj)
    return results

if run_all:
    results = run_tests(plugin_list, list(range(len(all_scenarios))), mode, api_endpoint, api_key)
    st.session_state["results"] = results
    st.success("All tests complete!")
elif run_selected:
    if selected_plugins and selected_scenarios_idx:
        results = run_tests(selected_plugins, selected_scenarios_idx, mode, api_endpoint, api_key)
        st.session_state["results"] = results
        st.success("Selected tests complete!")
    else:
        st.warning("Select at least one plugin and one scenario.")

# === 6. REPORTING SECTION ===
if "results" in st.session_state:
    st.header("📊 View/Export Report")
    st.download_button(
        "⬇️ Download JSON Report",
        data=json.dumps(st.session_state["]()_
