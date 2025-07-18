"""
Context and reasoning tests: multi-turn, context shift, memory traps.
Inspired by Yair Neuman's AI context work.
"""

def test_context_understanding(scenario, api_client):
    # scenario: dict with "steps": [prompt1, prompt2, ...]
    history = []
    for idx, step in enumerate(scenario.get("steps", [])):
        response = api_client.chat(step)
        output = response["output"] if "output" in response else str(response)
        history.append({"step": idx + 1, "prompt": step, "output": output})
    # TODO: Add memory/confusion/contradiction detection
    return {"history": history}

