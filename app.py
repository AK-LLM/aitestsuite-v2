# app.py
"""
Root launcher for Streamlit Cloud and other platforms.
Ensures core, plugins, ui, etc. can be imported from the project root.
Runs your main UI in ui/streamlit_app.py.
"""

import os
import sys

# Ensure the current (repo root) directory is in the Python path
sys.path.append(os.path.dirname(__file__))

# Import and launch your Streamlit UI from ui/streamlit_app.py
from ui.streamlit_app import *
