from typing import Dict, Any, List
from tools import advice_for_metric, lifestyle_config
from guide_topics import topic_content, classify_topic

def execute(intent_id: str, slots: dict, profile: dict) -> Dict[str, Any]:
    """Trả response"""
    if intent_id == "greet.smalltalk":
        return {
            "no_data": False,
            "numbers": [],
            "classification": {},
            "actions": [],
            "cautions": [],
            "explanations": [
                "Xin chào! Mình có thể giúp bạn đọc kết quả xét nghiệm và cho lời khuyên hoặc hướng dẫn sử dụng web HMS."
            ],
        }

    if intent_id == "guide.query":
        topic_id = (slots or {}).get("topic_id") or classify_topic(profile.get("last_question", ""))
        topic = topic_content(topic_id) if topic_id else None
        if not topic:
            topic = {""}
        if not topic:
            return {
                "no_data": False,
                "numbers": [],
                "classification": {},
                "actions": [],
                "cautions": [],
                "explanations": ["Xin lỗi, mình chưa xác định được hướng dẫn. Hãy hỏi cụ thể hơn."],
                "targets": [],
            }
        parts: List[str] = [f"Hướng dẫn: {topic.get('title', 'Hướng dẫn')}"]
        steps = topic.get("steps", [])
        notes = topic.get("notes", [])
        if steps:
            parts.append(" • ".join(steps))
        if notes:
            parts.append("Lưu ý: " + " ".join(notes[:2]))
        return {
            "no_data": False,
            "numbers": [],
            "classification": {},
            "actions": [],
            "cautions": [],
            "explanations": [parts[0]],
            "targets": [" | ".join(parts[1:])] if len(parts) > 1 else [],
        }

    if intent_id == "lifestyle.advice":
        ls = lifestyle_config()
        actions: List[str] = (ls.get("diet_general", []) or []) + (ls.get("physical_activity", []) or [])
        cautions: List[str] = ls.get("general_warnings", []) or []
        return {
            "no_data": False,
            "numbers": [],
            "classification": {},
            "actions": actions[:6],
            "cautions": cautions[:4],
            "explanations": ["Khuyến nghị lối sống tổng quát."],
        }

    if intent_id == "vital.query":
        metric = (slots or {}).get("metric")
        info = advice_for_metric(metric, profile)
        number_val, number_unit, number_date = info.get("number", (None, None, None))

        numbers = []
        if number_val is not None:
            numbers.append({"name": metric, "value": number_val, "unit": number_unit, "date": number_date})

        explanations: List[str] = []
        if info.get("label"):
            explanations.append(f"Phân loại {info.get('title') or metric}: {info['label']}.")
        if number_val is not None:
            if number_unit:
                explanations.append(f"{(info.get('title') or metric).capitalize()} gần nhất: {number_val} {number_unit}" + (f" (ngày {number_date})." if number_date else "."))
            else:
                explanations.append(f"{(info.get('title') or metric).capitalize()} gần nhất: {number_val}" + (f" (ngày {number_date})." if number_date else "."))

        return {
            "no_data": False,
            "numbers": numbers,
            "classification": {},
            "actions": (info.get("tips") or [])[:6],
            "cautions": (info.get("cautions") or [])[:3],
            "explanations": explanations,
        }

    return {
        "no_data": True,
        "numbers": [],
        "classification": {},
        "actions": [],
        "cautions": [],
        "explanations": ["Xin lỗi, mình chưa biết trả lời câu này."],
    }
