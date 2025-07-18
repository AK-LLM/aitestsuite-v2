"""
Handles all LLM API interactions.
Supports: demo mode (returns canned results), or live mode (calls real APIs).
Add new API providers here as needed.
"""

import requests
import yaml
import os

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

class APIClient:
    def __init__(self, config):
        self.mode = config.get("mode", "demo")
        self.provider = config.get("api_provider", "openai")
        self.api_key = os.getenv("AITESTSUITE_API_KEY", config.get("api_key", ""))
        self.endpoint = config.get("api_endpoint", "")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def chat(self, prompt):
        if self.mode == "demo":
            return {"output": "This is a demo response.", "meta": {}}
        elif self.provider == "openai":
            resp = requests.post(
                self.endpoint,
                headers=self.headers,
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        else:
            raise NotImplementedError(f"Provider '{self.provider}' not implemented.")

