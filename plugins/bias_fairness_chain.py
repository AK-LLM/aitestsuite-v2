METADATA = {
    "name": "Bias and Cross-Demographic Fairness",
    "category": "bias",
    "description": "Tests prompt for cross-group stereotypes and fairness.",
    "risk": "Medium",
    "references": ["Bias", "NIST AI RMF"]
}

def run(scenario, api_client, endpoint=None):
    groups = scenario.get("groups", ["men", "women", "children", "non-binary"])
    outputs = {}
    prompt = scenario.get("prompt", "")
    for group in groups:
        prompt_text = prompt.replace("{group}", group) if "{group}" in prompt else prompt
        response = api_client.chat(prompt_text)
        outputs[group] = response.get("output", response)
    return outputs
