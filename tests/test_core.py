from core.api_client import APIClient, load_config

def test_demo_mode():
    config = load_config()
    config["mode"] = "demo"
    api_client = APIClient(config)
    out = api_client.chat("hello")
    assert "demo" in out["output"].lower()

