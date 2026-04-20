import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.forget import analyze_importance
text = sys.argv[1] if len(sys.argv) > 1 else ""
emotion = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {"type": "平静", "intensity": 5}
print(analyze_importance(text, emotion))
