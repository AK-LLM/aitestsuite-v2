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

config = load_config()
mode = st.sidebar.radio("Mode", ["demo", "live"])
config["mode"] = mode

# Endpoint/model selector
endpoint = st.sidebar.text_input("LLM Endpoint/Model", config.get("api_endpoint", ""))
if endpoint:
    config["api_endpoint"] = endpoint

api_client = APIClient(config)
plugins = discover_plugins()

# SCENARIO SOURCE
scenario_source = st.radio("Test Source", ["Prebuilt", "Manual"])
if scenario_source == "Prebuilt":
    scenario_files = [f for f in os.listdir("scenarios") if f.endswith(".json")]
    file = st.selectbox("Scenario file", scenario_files)
    if st.button("Load Scenarios"):
        scenarios = []
        try:
            path = os.path.join("scenarios", file)
            scenarios = load_scenarios(path)
            st.success(f"Loaded {len(scenarios)} scenarios from {file}.")
        except Exception as e:
            st.error(f"Error loading scenario file: {e}")
        for idx, scenario in enumerate(scenarios):
            st.markdown(f"#### Test {idx+1}: {scenario.get('name', '')}")
            # Defensive: show missing fields
            if "type" not in scenario:
                st.error(f"Scenario missing 'type' field: {scenario}")
                continue
            ptype = scenario.get("type", "uncategorized")
            # Defensive: match plugin by category (case-insensitive)
            plugin = next((p for p in plugins if p["category"].lower() in ptype.lower()), None)
            if plugin:
                if st.button(f"Run {scenario.get('name', '')}"):
                    try:
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
                            save_html(html_report, f"reports/{scenario.get('name', '')}.html")
                            st.success(f"Saved to reports/{scenario.get('name', '')}.html")
                    except Exception as e:
                        st.error(f"Error running scenario: {e}")
            else:
                st.warning(
                    f"No plug-in found for scenario type '{ptype}'. "
                    f"Scenario: {scenario}\n\n"
                    "Check your plug-in category matches your scenario 'type' field."
                )
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
                        save_html(html_report, "reports/manual_scenario.html")
                        st.success("Saved to reports/manual_scenario.html")
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
