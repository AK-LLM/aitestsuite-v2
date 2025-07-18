"""
Robustness: paraphrasing, fuzzing, adversarial examples, stress tests, shuffling, typos, unicode, etc.
"""

import random

def fuzz_prompt(prompt):
    # Simple fuzz: add random typos
    words = prompt.split()
    if len(words) < 2:
        return prompt
    idx = random.randint(0, len(words)-1)
    words[idx] = words[idx][::-1]  # Reverse a word
    return " ".join(words)

def robustness_suite(prompt, api_client):
    adversarial_prompts = [
        prompt,
        fuzz_prompt(prompt),
        prompt.upper(),
        prompt.replace("not", "definitely not"),
        prompt + " \u202e",  # Unicode trick
    ]
    results = []
    for adv in adversarial_prompts:
        response = api_client.chat(adv)
        results.append({"input": adv, "output": response["output"]})
    return {"results": results}
