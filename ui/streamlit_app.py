import streamlit as st
import os
import json
import yaml

from core.api_client import APIClient, load_config
from core.plugin_loader import discover_plugins
from core.scenario_loader import load_scenarios
from core.reporting import generate_report, save_html

st.set_page_config(page_title="AI Test Suite v2 (Red Team Max)", layout="wide")
st.title("🛡️ AI Test Suite v2 (Red Team Max)")

# ==== Ensure all folders exist (robust startup) ====
for folder in ["scenarios", "plugins", "reports"]:
    if not os.path.exists(folder):
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception as e:
            st.error(f"Required folder '{folder}' could not be created: {e}")

# Defensive: global exception hook (shows any top-level Python crash)
import sys
def global_exception_hook(exctype, value, traceback):
    st.error(f"Unhandled Exception: {value}")
    sys.__excepthook__(exctype, value, traceback)
sys.excepthook = global_exception_hook

# ==== Load Config ====
try:
    config = load_config()
except Exception as e:
    st.error(f"Error loading config: {e}")
    config = {}

# ==== Mode and API ====
try:
    mode = st.sidebar.radio("Mode", ["demo", "live"], index=0)
    config["mode"] = mode
except Exception as e:
    st.error(f"Sidebar mode error: {e}")
    mode = "demo"
    config["mode"] = mode

try:
    endpoint = st.sidebar.text_input("LLM Endpoint/Model", config.get("api_endpoint", ""))
    if endpoint:
        config["api_endpoint"] = endpoint
except Exception as e:
    st.error(f"Sidebar endpoint error: {e}")

# ==== Init API client ====
try:
    api_client = APIClient(config)
except Exception as e:
    st.error(f"APIClient init error: {e}")
    api_client = None

# ==== Discover Plugins ====
try:
    plugins = discover_plugins()
except Exception as e:
    st.error(f"Plug-in discovery error: {e}")
    plugins = []
if not plugins:
    st.warning("No plug-ins found! Check your /plugins/ directory and plug-in format.")

# ==== Scenario Source ====
try:
    scenario_source = st.radio("Test Source", ["Prebuilt", "Manual"])
except Exception as e:
    st.error(f"Scenario source selector error: {e}")
    scenario_source = "Prebuilt"

if scenario_source == "Prebuilt":
    try:
        scenario_files = [f for f in os.listdir("scenarios") if f.endswith(".json")]
        if not scenario_files:
            st.error("No scenario files found in /scenarios/")
        else:
            file = st.selectbox("Scenario file", scenario_files)
            if st.button("Load Scenarios"):
                scenarios = []
                try:
                    path = os.path.join("scenarios", file)
                    scenarios = load_scenarios(path)
                    st.success(f"Loaded {len(scenarios)} scenarios from {file}.")
                except Exception as e:
                    st.error(f"Error loading scenario file: {e}")
                    scenarios = []
                for idx, scenario in enumerate(scenarios):
                    st.markdown(f"#### Test {idx+1}: {scenario.get('name', '')}")
                    if "type" not in scenario:
                        st.error(f"Scenario missing 'type' field: {scenario}")
                        continue
                    ptype = scenario.get("type", "uncategorized")
                    # Case-insensitive, partial match OK
                    plugin = next((p for p in plugins if p["category"].lower() in ptype.lower()), None)
                    if plugin:
                        if st.button(f"Run {scenario.get('name', '')}"):
                            try:
                                if not api_client:
                                    st.error("API client not initialized.")
                                    continue
                                result = plugin["module"].run(scenario, api_client, endpoint)
                                st.json(result)
                                html_report = generate_report([{
                                    "scenario": scenario,
                                    "plugin": plugin["name"],
                                    "result": result,
                                    "risk": plugin["risk"],
                                    "references": plugin["references"]
                                }])
                                if st.button(f"Export {scenario.get('name', '')} Report"):
                                    try:
                                        save_html(html_report, f"reports/{scenario.get('name', '')}.html")
                                        st.success(f"Saved to reports/{scenario.get('name', '')}.html")
                                    except Exception as e:
                                        st.error(f"Error saving HTML report: {e}")
                            except Exception as e:
                                st.error(f"Error running scenario: {e}")
                    else:
                        st.warning(
                            f"No plug-in found for scenario type '{ptype}'. "
                            f"Scenario: {scenario}\n\n"
                            "Check your plug-in category matches your scenario 'type' field."
                        )
    except Exception as e:
        st.error(f"Error in prebuilt scenario UI: {e}")

else:
    st.info("Paste single scenario (JSON/YAML, must have `prompt` or `steps` and `type` field).")
    manual = st.text_area("Manual scenario")
    if st.button("Validate & Run Manual Scenario"):
        try:
            if manual.strip().startswith("{"):
                scenario = json.loads(manual)
            else:
                scenario = yaml.safe_load(manual)
            st.success("Scenario valid.")
            if "type" not in scenario:
                st.error(f"Manual scenario missing 'type' field: {scenario}")
            else:
                ptype = scenario.get("type", "uncategorized")
                plugin = next((p for p in plugins if p["category"].lower() in ptype.lower()), None)
                if plugin:
                    if not api_client:
                        st.error("API client not initialized.")
                    else:
                        result = plugin["module"].run(scenario, api_client, endpoint)
                        st.json(result)
                        html_report = generate_report([{
                            "scenario": scenario,
                            "plugin": plugin["name"],
                            "result": result,
                            "risk": plugin["risk"],
                            "references": plugin["references"]
                        }])
                        if st.button("Export Manual Scenario Report"):
                            try:
                                save_html(html_report, "reports/manual_scenario.html")
                                st.success("Saved to reports/manual_scenario.html")
                            except Exception as e:
                                st.error(f"Error saving HTML report: {e}")
                else:
                    st.warning(
                        f"No plug-in found for type '{ptype}'. "
                        f"Scenario: {scenario}\n\n"
                        "Check your plug-in category matches your scenario 'type' field."
                    )
        except Exception as e:
            st.error(f"Manual scenario invalid or error running scenario: {e}")

st.markdown("---")
st.markdown("**All results and reports will be saved in the `/reports/` folder for sharing, compliance, or further analysis.**")
