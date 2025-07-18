# /core/plugin_loader.py
"""
Auto-discovers all plug-ins and test modules in /core and /plugins.
Each plug-in/test must have:
    - 'run' function (takes prompt/scenario, api_client, returns result dict)
    - Metadata: 'name', 'description', 'category', 'risk', 'references'
Loads into registry for UI/CLI/batch runners.
"""

import importlib.util
import os

PLUGIN_FOLDERS = ["core", "plugins"]

def discover_plugins():
    registry = []
    for folder in PLUGIN_FOLDERS:
        for fname in os.listdir(folder):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            path = os.path.join(folder, fname)
            module_name = f"{folder}.{fname[:-3]}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                if hasattr(mod, "run") and hasattr(mod, "METADATA"):
                    registry.append({
                        "module": mod,
                        "name": mod.METADATA.get("name", fname),
                        "category": mod.METADATA.get("category", "uncategorized"),
                        "description": mod.METADATA.get("description", ""),
                        "risk": mod.METADATA.get("risk", ""),
                        "references": mod.METADATA.get("references", []),
                        "file": fname
                    })
            except Exception as e:
                print(f"Error loading plugin {fname}: {e}")
    return registry

# Example plug-in signature for /plugins/adv_prompt_chain.py:
"""
METADATA = {
    "name": "Advanced Prompt Chain Injection",
    "category": "Injection/Chaining",
    "description": "Chained injections bypassing model context buffer.",
    "risk": "Critical",
    "references": ["OWASP LLM01", "OpenAI Evals", "Anthropic Jailbreaks"]
}

def run(scenario, api_client):
    # Your chained attack logic here
    pass
"""
