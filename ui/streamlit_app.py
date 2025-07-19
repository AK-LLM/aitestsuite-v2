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
                st.write("DEBUG: Load Scenarios button clicked")
                scenarios = []
                try:
                    path = os.path.join("scenarios", file)
                    st.write(f"DEBUG: Loading scenarios from {path}")
                    scenarios = load_scenarios(path)
                    st.write(f"DEBUG: Loaded {len(scenarios)} scenarios")
                    st.success(f"Loaded {len(scenarios)} scenarios from {file}.")
                except Exception as e:
                    st.error(f"Error loading scenario file: {e}")
                    st.text(traceback.format_exc())
                    scenarios = []
                for idx, scenario in enumerate(scenarios):
                    st.write(f"DEBUG: Scenario {idx+1} - {scenario.get('name','')}")
                    st.markdown(f"#### Test {idx+1}: {scenario.get('name', '')}")
                    if "type" not in scenario:
                        st.error(f"Scenario missing 'type' field: {scenario}")
                        continue
                    ptype = scenario.get("type", "uncategorized")
                    plugin = next((p for p in plugins if p["category"].lower() in ptype.lower()), None)
                    st.write(f"DEBUG: Plugin match for type '{ptype}': {plugin['name'] if plugin else None}")
                    if plugin:
                        if st.button(f"Run {scenario.get('name', '')}"):
                            st.write(f"DEBUG: Running scenario {scenario.get('name', '')} with plugin {plugin['name']}")
                            try:
                                if not api_client:
                                    st.error("API client not initialized.")
                                    continue
                                try:
                                    result = plugin["module"].run(scenario, api_client, endpoint)
                                    st.json(result)
                                    st.write("DEBUG: Plug-in run complete")
                                except Exception as e:
                                    st.error(f"Error running scenario: {e}")
                                    st.text(traceback.format_exc())
                                    continue
                                try:
                                    html_report = generate_report([{
                                        "scenario": scenario,
                                        "plugin": plugin["name"],
                                        "result": result,
                                        "risk": plugin["risk"],
                                        "references": plugin["references"]
                                    }])
                                    st.write("DEBUG: Report generated")
                                    if st.button(f"Export {scenario.get('name', '')} Report"):
                                        try:
                                            save_html(html_report, f"reports/{scenario.get('name', '')}.html")
                                            st.success(f"Saved to reports/{scenario.get('name', '')}.html")
                                            st.write("DEBUG: Report saved")
                                        except Exception as e:
                                            st.error(f"Error saving HTML report: {e}")
                                            st.text(traceback.format_exc())
                                except Exception as e:
                                    st.error(f"Report generation error: {e}")
                                    st.text(traceback.format_exc())
                            except Exception as e:
                                st.error(f"Error in scenario run block: {e}")
                                st.text(traceback.format_exc())
                    else:
                        st.warning(
                            f"No plug-in found for scenario type '{ptype}'. "
                            f"Scenario: {scenario}\n\n"
                            "Check your plug-in category matches your scenario 'type' field."
                        )
    except Exception as e:
        st.error(f"Error in prebuilt scenario UI: {e}")
        st.text(traceback.format_exc())

else:
    st.info("Paste single scenario (JSON/YAML, must have `prompt` or `steps` and `type` field).")
    manual = st.text_area("Manual scenario")
    if st.button("Validate & Run Manual Scenario"):
        st.write("DEBUG: Manual scenario button clicked")
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
                st.write(f"DEBUG: Plugin match for manual scenario type '{ptype}': {plugin['name'] if plugin else None}")
                if plugin:
                    if not api_client:
                        st.error("API client not initialized.")
                    else:
                        try:
                            result = plugin["module"].run(scenario, api_client, endpoint)
                            st.json(result)
                            st.write("DEBUG: Manual scenario plug-in run complete")
                        except Exception as e:
                            st.error(f"Error running manual scenario: {e}")
                            st.text(traceback.format_exc())
                            return
                        try:
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
                                    st.write("DEBUG: Manual scenario report saved")
                                except Exception as e:
                                    st.error(f"Error saving HTML report: {e}")
                                    st.text(traceback.format_exc())
                        except Exception as e:
                            st.error(f"Manual scenario report generation error: {e}")
                            st.text(traceback.format_exc())
                else:
                    st.warning(
                        f"No plug-in found for type '{ptype}'. "
                        f"Scenario: {scenario}\n\n"
                        "Check your plug-in category matches your scenario 'type' field."
                    )
        except Exception as e:
            st.error(f"Manual scenario invalid or error running scenario: {e}")
            st.text(traceback.format_exc())

st.markdown("---")
st.markdown("**All results and reports will be saved in the `/reports/` folder for sharing, compliance, or further analysis.**")
st.write("DEBUG: End of app file")
