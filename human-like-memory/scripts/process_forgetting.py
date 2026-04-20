import sys, os, json, tempfile
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "memory.json")

IMPORTANCE_LEVELS = {
    1:  (3,   14,  30),
    2:  (4,   18,  45),
    3:  (5,   22,  60),
    4:  (6,   28,  90),
    5:  (7,   35,  120),
    6:  (10,  45,  150),
    7:  (15,  60,  200),
    8:  (25,  90,  250),
    9:  (40,  120, 300),
    10: (60,  180, 365),
}

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

def get_decay_days(level, importance):
    base = IMPORTANCE_LEVELS.get(importance, IMPORTANCE_LEVELS[5])
    if level == 3:
        return base[0]
    elif level == 2:
        return base[1]
    elif level == 1:
        return base[2]

def process_forgetting():
    memory = read_json(MEMORY_FILE, default={})
    if not memory:
        return

    now = datetime.now()
    changed = False

    for key, event in list(memory.items()):
        last_accessed = event.get("last_accessed", event.get("level2", {}).get("时间", ""))
        if isinstance(last_accessed, str):
            try:
                last_accessed = datetime.fromisoformat(last_accessed)
            except:
                last_accessed = now
        elif not isinstance(last_accessed, datetime):
            last_accessed = now

        importance = event.get("重要性", 5)
        days_passed = (now - last_accessed).days

        l1_days = get_decay_days(1, importance)
        if days_passed >= l1_days:
            del memory[key]
            changed = True
            continue

        l2_days = get_decay_days(2, importance)
        if days_passed >= l2_days:
            if "level2_faded" not in event:
                event["level2_faded"] = True
                changed = True

        l3_days = get_decay_days(3, importance)
        if days_passed >= l3_days:
            if "level3_faded" not in event:
                original = event.get("level3", "")
                if len(original) > 10:
                    event["level3_faded"] = True
                    event["level3"] = original[:10] + "..."
                changed = True

    if changed:
        write_json(MEMORY_FILE, memory)

if __name__ == "__main__":
    process_forgetting()
