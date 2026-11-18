import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)

for d in [grandparent_dir, parent_dir, current_dir]:
    if d and d not in sys.path:
        sys.path.insert(0, d)

try:
    from backend.app import app
except ImportError:
    from app import app
