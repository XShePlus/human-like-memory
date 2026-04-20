import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.memorise import store_event
key = sys.argv[1] if len(sys.argv) > 1 else "未命名"
data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
store_event(key, data)
