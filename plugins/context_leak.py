def run(scenario, endpoint, apikey, mode, **kwargs):
    if mode.startswith("Demo"):
        return {
            "risk_level": "High Risk",
            "issue": "Context carryover: model leaked previous turn secrets (Demo)",
            "recommendation": "Enforce turn/session isolation."
        }
    return {
        "risk_level": "High Risk",
        "issue": "Context leak simulated (live).",
        "recommendation": "Investigate for memory bleed."
    }
