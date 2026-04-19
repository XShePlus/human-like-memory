import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.tools import Tools # type: ignore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "memory.json")

tools = Tools()

def read_synopsis():
    return list(tools.read_json(MEMORY_FILE, default={}).keys())
