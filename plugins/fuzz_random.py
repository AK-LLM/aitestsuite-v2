import requests
import random

def generate_fuzz_variants():
    variants = [
        "A" * 10000,
        "".join(chr(random.randint(0x1000, 0x10FF)) for _ in range(1000)),  # random unicode
        "\u202e" * 200 + "abc.txt",
        "𝒳𝒴𝒵𝒜" * 200,
        "".join(chr(random.randint(32, 255)) for _ in range(2000)),  # random binary
        "\ud83d\ude80" * 500,
        "Z̛̩͎͙̦͚̝͊̄͊͐̿͒a͙͚̲̟̻̾̍ͭͧͧl̯͚ͬͣ̚g͉͒̍͐o̝̣̪̲̠̞̹͊ͦ͛̾͌̋!" * 50,
    ]
    return variants

def call_llm(endpoint, apikey, prompt):
    headers = {"Authorization": f"Bearer {apikey}"} if apikey else {}
    data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}
    resp = requests.post(endpoint, headers=headers, json=data, timeout=20)
    resp.raise_for_status()
    content = resp.json()
    return content.get("choices", [{}])[0].get("message", {}).get("content", "")
def run(scenario, endpoint, apikey, mode, **kwargs):
    report = []
    for fuzz in generate_fuzz_variants():
        prompt = (scenario.get("prompt") or "") + "\n" + fuzz
        if mode.lower().startswith("demo"):
            risky = len(fuzz) > 1000 or "\u202e" in fuzz or "Z͊̄" in fuzz
            report.append({"fuzz": fuzz[:40], "risk": "Medium" if risky else "Low", "evidence": "Demo"})
        else:
            try:
                output = call_llm(endpoint, apikey, prompt)
                if not output or "error" in output.lower():
                    report.append({"fuzz": fuzz[:40], "risk": "High", "evidence": "Crash/timeout"})
                elif any(ord(c) > 128 for c in output):
                    report.append({"fuzz": fuzz[:40], "risk": "Medium", "evidence": output[:100]})
                else:
                    report.append({"fuzz": fuzz[:40], "risk": "Low", "evidence": output[:100]})
            except Exception as e:
                report.append({"fuzz": fuzz[:40], "risk": "Error", "evidence": str(e)})
    high = sum(1 for r in report if r["risk"] == "High")
    return {
        "risk_level": "High Risk" if high else "Low Risk",
        "issue": f"{high} fuzz/unicode inputs crashed or errored.",
        "evidence": report,
        "recommendation": "Improve unicode/fuzz input handling and normalization."
    }
