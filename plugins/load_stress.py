import requests
import time

def call_llm(endpoint, apikey, prompt):
    headers = {"Authorization": f"Bearer {apikey}"} if apikey else {}
    data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}
    resp = requests.post(endpoint, headers=headers, json=data, timeout=10)
    resp.raise_for_status()
    content = resp.json()
    return content.get("choices", [{}])[0].get("message", {}).get("content", "")
def run(scenario, endpoint, apikey, mode, **kwargs):
    prompt = scenario.get("prompt") or "Say hello!"
    total = 30
    errors, latencies = 0, []
    for _ in range(total):
        t0 = time.time()
        try:
            if mode.lower().startswith("demo"):
                latency = 0.2
            else:
                call_llm(endpoint, apikey, prompt)
                latency = time.time() - t0
            latencies.append(latency)
        except Exception:
            errors += 1
            latencies.append(None)
    avg_latency = sum([l for l in latencies if l]) / max(1, len([l for l in latencies if l]))
    return {
        "risk_level": "High Risk" if errors > 5 else "Medium Risk" if errors > 1 else "Low Risk",
        "issue": f"{errors} errors in {total} rapid requests, avg latency {avg_latency:.2f}s",
        "recommendation": "Implement rate limits, scale out infra, audit logs."
    }
