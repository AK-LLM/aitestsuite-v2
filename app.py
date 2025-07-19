import os
import sys

# Ensure the root and all subdirs are in Python's path
sys.path.append(os.path.dirname(__file__))

# Import and run your real Streamlit app from ui/
from ui.streamlit_app import *
