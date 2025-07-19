# aitestsuite-v2/plugins/bias_fairness_chain.py
METADATA = {
    "name": "Bias and Cross-Demographic Fairness",
    "category": "bias",
    "description": "Tests prompt for cross-group stereotypes and fairness using demographic substitution.",
    "risk": "Medium",
    "references": ["Bias", "NIST AI RMF"]
}

def run(scenario, api_client, endpoint=None):
    groups = scenario.get("groups", ["men", "women", "children", "non-binary"])
    outputs = {}
    for group in groups:
        prompt = scenario["prompt"].replace("{group}", group)
        response = api_client.chat(prompt)
        outputs[group] = response["output"]
    return outputs
