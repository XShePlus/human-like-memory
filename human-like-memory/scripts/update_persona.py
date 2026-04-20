import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.memorise import update_persona
traits = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
update_persona(traits)
