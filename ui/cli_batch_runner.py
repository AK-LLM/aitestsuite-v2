"""
Batch CLI runner for aitestsuite-v2.
- Runs all scenarios in selected file or folder.
- Supports endpoint/model targeting per scenario or batch.
- Generates advanced HTML/PDF/CSV reports with legend, risk mapping, and charts.
"""
import argparse
import os
import json
from core.api_client import APIClient, load_config
from core.plugin_loader import discover_plugins
from core.scenario_loader import load_scenarios
from core.reporting import generate_report, save_html, save_pdf, save_csv

def run_scenario_with_plugin(scenario, plugin, api_client, endpoint=None):
    # Each plugin must have a 'run' function taking (scenario, api_client, endpoint)
    try:
        result = plugin['module'].run(scenario, api_client, endpoint)
        return {
            "scenario": scenario,
            "plugin": plugin["name"],
            "result": result,
            "risk": plugin["risk"],
            "references": plugin["references"]
        }
    except Exception as e:
        return {
            "scenario": scenario,
            "plugin": plugin["name"],
            "error": str(e),
            "risk": "Critical",
            "references": plugin["references"]
        }

def batch_run(scenario_files, api_client, endpoint=None):
    plugins = discover_plugins()
    results = []
    for file in scenario_files:
        print(f"Loading: {file}")
        scenarios = load_scenarios(file)
        for scenario in scenarios:
            print(f"\n[TEST] {scenario.get('name','')}")
            # Find plugin for this scenario type
            ptype = scenario.get("type", "uncategorized")
            plugin = next((p for p in plugins if p["category"].lower() in ptype.lower()), None)
            if plugin:
                result = run_scenario_with_plugin(scenario, plugin, api_client, endpoint)
                results.append(result)
                print(f"Risk: {result.get('risk','?')} | Plugin: {plugin['name']}")
            else:
                print(f"WARNING: No plugin for scenario type '{ptype}'")
    return results

def main():
    parser = argparse.ArgumentParser(description="AI Test Suite Batch Runner")
    parser.add_argument("--mode", choices=["demo", "live"], default="live")
    parser.add_argument("--scenario", type=str, help="Scenario JSON or folder", required=True)
    parser.add_argument("--endpoint", type=str, default=None, help="LLM API endpoint override (optional)")
    parser.add_argument("--export", choices=["html", "pdf", "csv"], default="html")
    args = parser.parse_args()

    config = load_config()
    config["mode"] = args.mode
    if args.endpoint:
        config["api_endpoint"] = args.endpoint
    api_client = APIClient(config)

    # Allow folder of scenarios or single file
    if os.path.isdir(args.scenario):
        files = [os.path.join(args.scenario, f) for f in os.listdir(args.scenario) if f.endswith(".json")]
    else:
        files = [args.scenario]

    all_results = batch_run(files, api_client, endpoint=args.endpoint)
    summary_report = generate_report(all_results)

    out_path = f"reports/batch_report.{args.export}"
    if args.export == "html":
        save_html(summary_report, out_path)
    elif args.export == "pdf":
        save_pdf(summary_report, out_path)
    elif args.export == "csv":
        save_csv(summary_report, out_path)
    print(f"Report exported to {out_path}")

if __name__ == "__main__":
    main()
