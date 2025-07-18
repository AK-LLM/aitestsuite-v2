import streamlit as st
from core.api_client import APIClient, load_config
from core.security import classic_prompt_injection_test, role_confusion_test
from core.robustness import robustness_suite
from core.context import context_switch_scenario
from core.bias import stereotype_test, cross_demographic_fairness_test
from core.reporting import save_html, save_pdf
from core.scenario_loader import load_scenarios

st.set_page_config(page_title="AI Test Suite v2", layout="wide")
st.title("🛡️ AI Test Suite v2 (Production)")

config = load_config()
api_client = APIClient(config)

mode = st.sidebar.radio("Mode", ["demo", "live"])
config["mode"] = mode

scenario_file = st.sidebar.selectbox(
    "Scenario File",
    ["sample_scenarios.json", "prompt_injection.json", "context_shift.json"]
)
scenarios = load_scenarios(f"scenarios/{scenario_file}")

for idx, scenario in enumerate(scenarios):
    st.markdown(f"### Test {idx+1}: {scenario['name']}")
    if scenario.get("type") == "security":
        result = classic_prompt_injection_test(scenario["prompt"], api_client)
        st.json(result)
    elif scenario.get("type") == "robustness":
        result = robustness_suite(scenario["prompt"], api_client)
        st.json(result)
    elif scenario.get("type") == "context":
        result = context_switch_scenario(scenario, api_client)
        st.json(result)
    elif scenario.get("type") == "bias":
        result = stereotype_test(scenario["prompt"], api_client)
        st.json(result)
    elif scenario.get("type") == "cross_demographic":
        groups = scenario.get("groups", ["men", "women", "children"])
        result = cross_demographic_fairness_test(scenario["prompt"], groups, api_client)
        st.json(result)
    else:
        st.warning("Unknown scenario type.")
        continue

    col1, col2 = st.columns(2)
    if col1.button(f"Export as HTML (Test {idx+1})"):
        save_html(result, f"reports/report_{idx+1}.html")
        st.success(f"Saved to reports/report_{idx+1}.html")
    if col2.button(f"Export as PDF (Test {idx+1})"):
        save_pdf(result, f"reports/report_{idx+1}.pdf")
        st.success(f"Saved to reports/report_{idx+1}.pdf")
