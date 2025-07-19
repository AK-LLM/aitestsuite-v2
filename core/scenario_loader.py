import os
import json
import yaml

def load_scenarios(path):
    """
    Loads scenarios from a JSON or YAML file.
    Returns a list of scenario dicts.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Scenario file not found: {path}")

    _, ext = os.path.splitext(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            if ext.lower() in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"Scenarios file must contain a list of scenarios. Got: {type(data)}")
        for idx, sc in enumerate(data):
            if "type" not in sc:
                raise ValueError(f"Scenario #{idx+1} missing required 'type' field: {sc}")
        return data
    except Exception as e:
        print(f"[Scenario Loader] Error loading '{path}': {e}")
        raise
