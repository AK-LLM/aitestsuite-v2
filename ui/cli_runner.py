"""
Simple CLI runner for aitestsuite-v2
"""
import argparse
from core.api_client import APIClient, load_config
from core.scenario_loader import load_scenarios
from core.security import test_prompt_injection
from core.context import test_context_understanding
from core.bias import test_bias_toxicity

def main():
    parser = argparse.ArgumentParser(description="AI Test Suite CLI")
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--scenario", type=str, default="scenarios/sample_scenarios.json")
    args = parser.parse_args()

    config = load_config()
    config["mode"] = args.mode
    api_client = APIClient(config)
    scenarios = load_scenarios(args.scenario)

    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        if scenario.get("type") == "security":
            result = test_prompt_injection(scenario["prompt"], api_client)
        elif scenario.get("type") == "context":
            result = test_context_understanding(scenario, api_client)
        elif scenario.get("type") == "bias":
            result = test_bias_toxicity(scenario["prompt"], api_client)
        else:
            result = "Unknown scenario type."
        print(result)

if __name__ == "__main__":
    main()

