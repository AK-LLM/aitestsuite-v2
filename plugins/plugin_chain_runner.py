import os
import importlib.util

def run(scenario, endpoint, apikey, mode, **kwargs):
    plugin_dir = os.path.dirname(__file__)
    results = []
    for fname in os.listdir(plugin_dir):
        if fname.endswith('.py') and fname != os.path.basename(__file__):
            plugin_path = os.path.join(plugin_dir, fname)
            spec = importlib.util.spec_from_file_location("mod", plugin_path)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                out = mod.run(scenario, endpoint, apikey, mode)
                results.append({"plugin": fname, "out": out})
            except Exception as e:
                results.append({"plugin": fname, "out": str(e)})
    return {
        "risk_level": "High Risk" if any(r.get("out", {}).get("risk_level", "").startswith("High") for r in results) else "Low Risk",
        "issue": "Cross-plugin run completed.",
        "evidence": results,
        "recommendation": "Review all plugin outputs for aggregate risks."
    }
