import streamlit as st
import os
import json
import importlib.util
from datetime import datetime

# ---- CONFIG ----
SCENARIO_FOLDER = "scenarios"
PLUGIN_FOLDER = "plugins"
REPORT_FOLDER = "reports"

st.set_page_config(page_title="AI Test Suite v2 (Red Team Max)", layout="wide")
st.markdown("# 🛡️ AI Test Suite v2 (Red Team Max)")

# ---- SIDEBAR: Demo/Live Toggle and LLM Endpoint ----
st.sidebar.title("⚡ Test Execution Mode")
mode = st.sidebar.radio(
    "Choose mode:",
    ["Demo (offline/mock)", "Live (real API)"],
    index=0
)
is_live = mode == "Live (real API)"
llm_endpoint = st.sidebar.text_input(
    "LLM Endpoint/Model",
    value="https://api.openai.com/v1/chat/completions" if is_live else "",
    help="Set your API endpoint here for live mode"
)

# ---- 1. SCENARIO LOADER (Preset + Custom Upload) ----
st.markdown("## 🧪 Load Test Scenarios")
preset_scenarios = [
    f for f in os.listdir(SCENARIO_FOLDER)
    if f.endswith(".json")
]
selected_presets = st.multiselect(
    "Select scenario(s) from built-in library:",
    options=preset_scenarios,
    help="Choose from JSON files in the /scenarios folder"
)
uploaded_files = st.file_uploader(
    "Or upload custom scenario JSON(s)", type="json", accept_multiple_files=True
)

scenario_data = []
# Load preset scenarios
for scenario_file in selected_presets:
    try:
        with open(os.path.join(SCENARIO_FOLDER, scenario_file), "r", encoding="utf-8") as f:
            scenario_data.append(json.load(f))
    except Exception as e:
        st.warning(f"Error loading {scenario_file}: {e}")

# Load uploaded scenarios
for uploaded_file in uploaded_files or []:
    try:
        scenario_data.append(json.load(uploaded_file))
    except Exception as e:
        st.warning(f"Error loading uploaded file: {e}")

if not scenario_data:
    st.info("No valid scenarios loaded yet.")
else:
    st.success(f"Loaded {len(scenario_data)} scenario(s) for testing.")

# ---- 2. PLUGIN LOADER (Auto-import all plugins) ----
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
                except Exception as e:
                    st.warning(f"Error loading plugin {plugin_name}: {e}")
    return plugins

plugins = load_plugins(PLUGIN_FOLDER)

# ---- 3. PLUGIN MULTI-SELECT ----
st.markdown("## 💼 Select Attack/Testing Plugins")
all_plugin_names = sorted(list(plugins.keys()))
selected_plugins = st.multiselect(
    "Select plugins/tools to run (all by default):",
    options=all_plugin_names,
    default=all_plugin_names,
    help="Auto-detected from /plugins"
)

if not selected_plugins:
    st.warning("No plugins selected.")
else:
    st.success(f"{len(selected_plugins)} plugins ready for testing.")

# ---- 4. RUN TESTS ----
if st.button("🚀 RUN ALL TESTS/ATTACKS on ALL SCENARIOS", disabled=not scenario_data or not selected_plugins):
    results = []
    with st.spinner("Running full test suite..."):
        for scen_idx, scen in enumerate(scenario_data):
            scen_results = {"scenario": scen, "results": []}
            for plugin_name in selected_plugins:
                plugin = plugins.get(plugin_name)
                if plugin:
                    try:
                        # Assumes each plugin has a run() method taking scenario as input
                        result = plugin.run(scen)
                        scen_results["results"].append({
                            "plugin": plugin_name,
                            "result": result
                        })
                    except Exception as e:
                        scen_results["results"].append({
                            "plugin": plugin_name,
                            "result": f"Error: {e}"
                        })
            results.append(scen_results)
        st.success("All tests complete!")
        st.session_state["results"] = results
        st.balloons()

# ---- 5. REPORTING ----
def save_report(results):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = os.path.join(REPORT_FOLDER, f"ai_test_report_{ts}.json")
    os.makedirs(REPORT_FOLDER, exist_ok=True)
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return outpath

if "results" in st.session_state:
    st.markdown("---\n### 📊 View/Export Report")
    if st.button("💾 Download JSON Report"):
        report_path = save_report(st.session_state["results"])
        with open(report_path, "rb") as f:
            st.download_button(
                label="Download Full Report",
                data=f,
                file_name=os.path.basename(report_path),
                mime="application/json"
            )

    # Simple table view
    for scen_idx, scen_result in enumerate(st.session_state["results"]):
        st.markdown(f"#### Scenario {scen_idx + 1}")
        for r in scen_result["results"]:
            st.write(f"**Plugin:** {r['plugin']} | **Result:** {r['result']}")

# ---- 6. HELP/FOOTER ----
st.markdown("""
---
#### 💡 Tips:
- Place new JSON scenario files in `/scenarios` to expand your test library.
- Add new plugins (.py) in `/plugins`—each should define a `run(scenario)` function.
- Results are saved in `/reports`. You can extend reporting as needed!
""")

