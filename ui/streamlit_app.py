import streamlit as st
import yaml
from core.api_client import APIClient, load_config
from core.security import test_prompt_injection
from core.robustness import test_robustness
from core.context import test_context_understanding
from core.bias import test_bias_toxicity
from core.reporting import save_html
from core.scenario_loader import load_scenarios

st.set_page_config(page_title="AI Test Suite v2", layout="wide")
st.title("🛡️ AI Test Suite v2")

# Load config
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
        result = test_prompt_injection(scenario["prompt"], api_client)
    elif scenario.get("type") == "context":
        result = test_context_understanding(scenario, api_client)
    elif scenario.get("type") == "bias":
        result = test_bias_toxicity(scenario["prompt"], api_client)
    else:
        result = "Unknown scenario type."
    st.write(result)

    if st.button(f"Export Result {idx+1}"):
        save_html(str(result), f"reports/report_{idx+1}.html")
        st.success(f"Report saved to reports/report_{idx+1}.html")

