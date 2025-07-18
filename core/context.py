"""
Advanced context testing: multi-turn, context loss, memory, reasoning traps, Neuman-inspired.
"""

def context_switch_scenario(scenario, api_client):
    history = []
    # Each step may have a persona/context switch
    for idx, step in enumerate(scenario.get("steps", [])):
        prompt = step.get("prompt") if isinstance(step, dict) else step
        system = step.get("system", None) if isinstance(step, dict) else None
        previous = [{"role": "user", "content": h["prompt"]} for h in history]
        response = api_client.chat(prompt, system=system, history=previous)
        history.append({"step": idx+1, "prompt": prompt, "output": response["output"]})
    # Trap: look for contradiction, context confusion, persona leak
    contradictions = []
    outputs = [h["output"] for h in history]
    for i in range(1, len(outputs)):
        if outputs[i] != "" and outputs[i-1] != "" and outputs[i] == outputs[i-1]:
            contradictions.append(f"Same response for different persona at step {i+1}")
    return {"history": history, "contradictions": contradictions}
