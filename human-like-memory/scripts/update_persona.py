import sys, os, json, tempfile

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

def update_persona(traits):
    persona = read_json(PERSONA_FILE, default={"性格": {}, "爱好": {}, "习惯": {}, "价值观": {}})

    total = sum(
        sum(t["来源次数"] for t in cat.values())
        for cat in persona.values()
        if isinstance(cat, dict)
    )
    total = max(total, 1)

    for category, items in traits.items():
        if category not in persona:
            persona[category] = {}
        for trait, conf in items.items():
            if trait in persona[category]:
                persona[category][trait]["来源次数"] += 1
            else:
                persona[category][trait] = {
                    "置信度": conf if isinstance(conf, float) else 0.5,
                    "来源次数": 1
                }

    total = sum(
        sum(t["来源次数"] for t in cat.values())
        for cat in persona.values()
        if isinstance(cat, dict)
    )
    total = max(total, 1)

    for category in persona.values():
        if isinstance(category, dict):
            for trait in category.values():
                trait["置信度"] = trait.get("来源次数", 1) / total

    write_json(PERSONA_FILE, persona)

if __name__ == "__main__":
    traits = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    update_persona(traits)
