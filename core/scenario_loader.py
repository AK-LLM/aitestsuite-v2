"""
Load scenarios from JSON or YAML.
"""
import os
import json
import yaml

def load_scenarios(file_path):
    if file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported scenario format")
