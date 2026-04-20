import sys, os, json

def analyze_importance(text, emotion):
    score = 5

    if emotion.get("intensity", 5) >= 8:
        score += 2
    elif emotion.get("intensity", 5) >= 6:
        score += 1

    high_impact_emotions = {"愤怒", "悲伤", "恐惧", "兴奋", "焦虑"}
    if emotion.get("type") in high_impact_emotions:
        score += 1

    EMOTIONAL_WORDS = {"在乎", "记得", "一直", "永远", "难忘", "深刻", "重要", "真的很", "特别", "非常", "极其"}
    BENEFIT_WORDS = {"健康", "钱", "工作", "收入", "身体", "家人", "朋友", "恋人", "感情", "安全"}
    RELATION_WORDS = {"妈妈", "爸爸", "家人", "老婆", "老公", "女朋友", "男朋友", "朋友", "同事", "老板", "老师"}
    CASUAL_WORDS = {"随便", "好像", "大概", "可能吧", "也没什么", "就那样", "无所谓"}

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

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else ""
    emotion = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {"type": "平静", "intensity": 5}
    print(analyze_importance(text, emotion))
