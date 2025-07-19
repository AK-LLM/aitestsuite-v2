# aitestsuite-v2/plugins/adversarial_fuzz.py
METADATA = {
    "name": "Adversarial Fuzz/Unicode Attack",
    "category": "robustness",
    "description": "Fuzzes input using Unicode, misspellings, and edge-case formatting to bypass filters.",
    "risk": "High",
    "references": ["Robustness", "LLM02"]
}

def run(scenario, api_client, endpoint=None):
    base = scenario.get("prompt", "")
    fuzz_inputs = [
        base,
        base[::-1],
        base.replace("admin", "adm1n"),
        base + " \u202E",
        "".join(chr(ord(c)+1) for c in base if c.isalpha()),
        base.upper(),
        base.replace("e", "3").replace("a", "@"),
    ]
    outputs = []
    for inp in fuzz_inputs:
        resp = api_client.chat(inp)
        outputs.append({"input": inp, "output": resp["output"]})
    return outputs
