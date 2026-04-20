import sys, os, json, tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "memory.json")

def read_json(filepath, default=[]):
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def write_json(filepath, data, indent=2, ensure_ascii=False):
    dir_path = os.path.dirname(os.path.abspath(filepath))
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    fd, temppath = tempfile.mkstemp(suffix='.json', prefix='tmp_', dir=dir_path or '.')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
        os.replace(temppath, filepath)
    except Exception:
        if os.path.exists(temppath):
            os.unlink(temppath)
        raise

def store_event(key, event_data):
    memory = read_json(MEMORY_FILE, default={})
    memory[key] = event_data
    write_json(MEMORY_FILE, memory)

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "未命名"
    data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    store_event(key, data)
