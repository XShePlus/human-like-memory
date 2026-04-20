import sys, os, json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA_FILE = os.path.join(BASE_DIR, "data", "persona.json")

def read_json(filepath, default=[]):
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def read_persona():
    return read_json(PERSONA_FILE, default={"性格": {}, "爱好": {}, "习惯": {}, "价值观": {}})

if __name__ == "__main__":
    print(read_persona())
