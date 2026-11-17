import os
import sys

# Ensure repository root is on sys.path so 'backend' is cleanly importable in Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import app

# Vercel Serverless Function entry point
# Exposes WSGI callable 'app'
