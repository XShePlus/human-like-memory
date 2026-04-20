import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.forget import bump_importance
key = sys.argv[1] if len(sys.argv) > 1 else ""
if key:
    bump_importance(key)
