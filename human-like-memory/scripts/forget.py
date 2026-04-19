import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from scripts.tools import Tools # type: ignore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "memory.json")

tools = Tools()

# ============================================================
# 艾宾浩斯遗忘曲线 — 遗忘时间对照表
# ============================================================
# 记忆保留率（基于艾宾浩斯原始数据）
# -----------------------------------------------------------
# 时间间隔      | 保留率  | 遗忘率
# -----------------------------------------------------------
# 20分钟       | 58%    | 42%
# 1小时        | 56%    | 44%
# 9小时        | 36%    | 64%
# 1天          | 34%    | 66%
# 2天          | 28%    | 72%
# 6天          | 25%    | 75%
# 31天（约1月） | 21%    | 79%
# ============================================================
#
# 本系统遗忘规则（结合重要性等级）：
#
# 重要性等级  | L3遗忘周期 | L2遗忘周期 | L1遗忘周期(全部遗忘)
# -----------------------------------------------------------
# 1（最低）   | 3天       | 14天       | 30天
# 2          | 4天       | 18天       | 45天
# 3          | 5天       | 22天       | 60天
# 4          | 6天       | 28天       | 90天
# 5（中等）   | 7天       | 35天       | 120天
# 6          | 10天      | 45天       | 150天
# 7          | 15天      | 60天       | 200天
# 8          | 25天      | 90天       | 250天
# 9          | 40天      | 120天      | 300天
# 10（最高）  | 60天      | 180天      | 365天（一年）
# -----------------------------------------------------------
#
# 重要性自动判断依据：
# - 情绪强度高（愤怒、兴奋、悲伤、恐惧）→ 基础重要性+2
# - 涉及人物关系（家人、朋友、恋人）→ 基础重要性+1
# - 涉及切身利益（健康、金钱、工作）→ 基础重要性+1
# - 描述详细、字数多 → 基础重要性+1
# - 带有情感词（"在乎"、"记得"、"一直"）→ 基础重要性+2
# - 随口一提、语气随意 → 基础重要性-1
# - 最终重要性范围：1-10
#
# 重复效应：
# - 用户重复提及同一事件，重要程度+1（上限10）
# - 重复越多，遗忘越慢（遗忘周期延长1.2倍）
#
# 遗忘顺序：
# 1. L3（原始描述）最先遗忘，内容逐渐模糊或简化为概要
# 2. L2（结构化）部分遗忘，主体/动作/对象逐渐模糊
# 3. L1（概要key）最后遗忘，达到遗忘周期上限时整个事件删除
# ============================================================

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

# 情感词 → 加分
EMOTIONAL_WORDS = {"在乎", "记得", "一直", "永远", "难忘", "深刻", "重要", "真的很", "特别", "非常", "极其"}
# 切身利益词 → 加分
BENEFIT_WORDS = {"健康", "钱", "工作", "收入", "身体", "家人", "朋友", "恋人", "感情", "安全"}
# 关系词 → 加分
RELATION_WORDS = {"妈妈", "爸爸", "家人", "老婆", "老公", "女朋友", "男朋友", "朋友", "同事", "老板", "老师"}
# 随口一说词 → 减分
CASUAL_WORDS = {"随便", "好像", "大概", "可能吧", "也没什么", "就那样", "无所谓"}

def analyze_importance(text, emotion):
    score = 5

    if emotion.get("intensity", 5) >= 8:
        score += 2
    elif emotion.get("intensity", 5) >= 6:
        score += 1

    high_impact_emotions = {"愤怒", "悲伤", "恐惧", "兴奋", "焦虑"}
    if emotion.get("type") in high_impact_emotions:
        score += 1

    text_lower = text

    for word in EMOTIONAL_WORDS:
        if word in text_lower:
            score += 2
            break

    for word in BENEFIT_WORDS:
        if word in text_lower:
            score += 1
            break

    for word in RELATION_WORDS:
        if word in text_lower:
            score += 1
            break

    if len(text) > 50:
        score += 1

    for word in CASUAL_WORDS:
        if word in text_lower:
            score -= 1
            break

    return max(1, min(score, 10))

def get_decay_days(level, importance):
    base = IMPORTANCE_LEVELS.get(importance, IMPORTANCE_LEVELS[5])
    if level == 3:
        return base[0]
    elif level == 2:
        return base[1]
    elif level == 1:
        return base[2]

def process_forgetting():
    memory = tools.read_json(MEMORY_FILE, default={})
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

        # L1全部遗忘
        l1_days = get_decay_days(1, importance)
        if days_passed >= l1_days:
            del memory[key]
            changed = True
            continue

        # L2部分遗忘
        l2_days = get_decay_days(2, importance)
        if days_passed >= l2_days:
            if "level2_faded" not in event:
                event["level2_faded"] = True
                changed = True

        # L3遗忘
        l3_days = get_decay_days(3, importance)
        if days_passed >= l3_days:
            if "level3_faded" not in event:
                original = event.get("level3", "")
                if len(original) > 10:
                    event["level3_faded"] = True
                    event["level3"] = original[:10] + "..."
                changed = True

    if changed:
        tools.write_json(MEMORY_FILE, memory)

def bump_importance(key):
    memory = tools.read_json(MEMORY_FILE, default={})
    if key in memory:
        memory[key]["重要性"] = min(memory[key].get("重要性", 5) + 1, 10)
        memory[key]["last_accessed"] = datetime.now().isoformat()
        tools.write_json(MEMORY_FILE, memory)
