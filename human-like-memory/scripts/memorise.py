import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.tools import Tools # type: ignore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "memory.json")
PERSONA_FILE = os.path.join(BASE_DIR, "data", "persona.json")

tools = Tools()

def read_persona():
    return tools.read_json(PERSONA_FILE, default={
        "性格": {}, "爱好": {}, "习惯": {}, "价值观": {}
    })

def store_event(key, event_data):
    # 读取已有记忆
    memory = tools.read_json(MEMORY_FILE, default={})
    # 写入新事件
    memory[key] = event_data
    tools.write_json(MEMORY_FILE, memory)

def update_persona(traits):
    # 读取已有画像
    persona = tools.read_json(PERSONA_FILE, default={
        "性格": {}, "爱好": {}, "习惯": {}, "价值观": {}
    })

    # 计算总分析次数（用于置信度）
    total = sum(
        sum(t["来源次数"] for t in cat.values())
        for cat in persona.values()
        if isinstance(cat, dict)
    )
    total = max(total, 1)

    # 更新各维度特征
    for category, items in traits.items():
        if category not in persona:
            persona[category] = {}

        for trait, conf in items.items():
            if trait in persona[category]:
                old = persona[category][trait]
                old["来源次数"] = old.get("来源次数", 0) + 1
            else:
                persona[category][trait] = {
                    "置信度": conf if isinstance(conf, float) else 0.5,
                    "来源次数": 1
                }

    # 重新计算所有置信度
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

    # 写回画像
    tools.write_json(PERSONA_FILE, persona)
