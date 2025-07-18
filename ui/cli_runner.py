"""
Batch CLI runner for aitestsuite-v2, runs all scenarios in selected file.
"""
import argparse
from core.api_client import APIClient, load_config
from core.scenario_loader import load_scenarios
from core.security import classic_prompt_injection_test, role_confusion_test
from core.context import context_switch_scenario
from core.robustness import robustness_suite
from core.bias import stereotype_test, cross_demographic_fairness_test
from core.reporting import save_html, save_txt, save_pdf, save_csv

def main():
    parser = argparse.ArgumentParser(description="AI Test Suite CLI")
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--scenario", type=str, default="scenarios/sample_scenarios.json")
    parser.add_argument("--export", choices=["html", "txt", "pdf", "csv"], default=None)
    args = parser.parse_args()

    config = load_config()
    config["mode"] = args.mode
    api_client = APIClient(config)
    scenarios = load_scenarios(args.scenario)
    all_results = []

    for idx, scenario in enumerate(scenarios):
        print(f"\n--- Test {idx+1}: {scenario['name']} ---")
        if scenario.get("type") == "security":
            result = classic_prompt_injection_test(scenario["prompt"], api_client)
        elif scenario.get("type") == "robustness":
            result = robustness_suite(scenario["prompt"], api_client)
        elif scenario.get("type") == "context":
            result = context_switch_scenario(scenario, api_client)
        elif scenario.get("type") == "bias":
            result = stereotype_test(scenario["prompt"], api_client)
        elif scenario.get("type") == "cross_demographic":
            groups = scenario.get("groups", ["men", "women", "children"])
            result = cross_demographic_fairness_test(scenario["prompt"], groups, api_client)
        else:
            result = {"error": "Unknown scenario type."}
        print(result)
        all_results.append(result)
        # Export after each test if requested
        if args.export:
            fname = f"reports/cli_report_{idx+1}.{args.export}"
            if args.export == "html":
                save_html(result, fname)
            elif args.export == "txt":
                save_txt(result, fname)
            elif args.export == "pdf":
                save_pdf(result, fname)
            elif args.export == "csv" and isinstance(result.get("results"), list):
                save_csv(result["results"], fname)
            print(f"Exported result to {fname}")

if __name__ == "__main__":
    main()
