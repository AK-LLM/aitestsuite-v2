"""
Scenario loader: loads test scenarios from JSON/YAML files.
"""

import json
import os

def load_scenarios(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

