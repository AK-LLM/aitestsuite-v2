"""
Robustness tests: adversarial attacks, paraphrasing, fuzzing, stress tests.
"""

def test_robustness(prompt, api_client):
    # Simple paraphrase test, replace with real attacks later
    adversarial_prompt = prompt.replace("not", "definitely not")
    response = api_client.chat(adversarial_prompt)
    output = response["output"] if "output" in response else str(response)
    # TODO: Add more perturbations, mutation, or stress tests
    return {"adversarial_prompt": adversarial_prompt, "output": output}

