"""
API client abstraction for calling any LLM. Supports demo (mock) and live modes.
Extensible for any provider (OpenAI, Azure, Claude, Ollama, etc).
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
        self.default_model = config.get("model", "gpt-3.5-turbo")

    def chat(self, prompt, system=None, history=None):
        if self.mode == "demo":
            # Demo output is "safe" for offline
            return {"output": f"[DEMO MODE] {prompt}", "meta": {"demo": True}}
        elif self.provider == "openai":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            if history:
                for msg in history:
                    messages.append(msg)
            messages.append({"role": "user", "content": prompt})
            resp = requests.post(
                self.endpoint,
                headers=self.headers,
                json={
                    "model": self.default_model,
                    "messages": messages,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            output = data["choices"][0]["message"]["content"]
            return {"output": output, "meta": {"provider": "openai"}}
        else:
            raise NotImplementedError(f"Provider '{self.provider}' not implemented.")
