import sys
import os

# --- Make sure the project root is in sys.path for all subfolder imports ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import runpy

# --- This will launch your main UI, just like running 'streamlit run ui/streamlit_app.py' ---
if __name__ == "__main__":
    runpy.run_path("ui/streamlit_app.py", run_name="__main__")
