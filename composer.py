from typing import Dict, Any, List
from models import Answer, AnswerStructured, NumberItem

def join_numbers(nums: List[dict]) -> str:
    parts: List[str] = []
    for n in nums:
        s = f"{n.get('name')}: {n.get('value')}{(' ' + n.get('unit')) if n.get('unit') else ''}"
        if n.get('date'):
            s += f" ({n.get('date')})"
        parts.append(s)
    return "; ".join(parts)

def compose(intent_id: str, payload: Dict[str, Any]) -> Answer:
    #note
    if payload.get("no_data") is True:
        text = payload.get("explanations", ["Xin lỗi, tôi chưa biết trả lời câu này."])[0]
        structured = AnswerStructured(
            conclusion="NO_DATA",
            numbers=[],
            trend=None,
            targets=[],
            actions=[],
            cautions=[],
            sources=[],
        )
        return Answer(text=text, structured=structured, confidence=0.6, meta={"intent": intent_id})

    explanations = payload.get("explanations", [])
    numbers = payload.get("numbers", [])
    targets = payload.get("targets", [])
    actions = payload.get("actions", [])
    cautions = payload.get("cautions", [])
    classification = payload.get("classification", {})

    text_parts: List[str] = []

    if explanations:
        text_parts.append(explanations[0])
    if numbers:
        text_parts.append(join_numbers(numbers))
    if targets:
        text_parts.append(targets[0])
    if actions:
        text_parts.append("Bạn nên: " + "; ".join(actions[:4]))
    if cautions:
        text_parts.append("Lưu ý: " + "; ".join(cautions[:2]))
    
    # print(text_parts)

    text = " | ".join([p for p in text_parts if p])

    structured = AnswerStructured(
        conclusion=explanations[0] if explanations else None,
        numbers=[NumberItem(**n) for n in numbers],
        trend=None,
        targets=targets,
        actions=actions,
        cautions=cautions,
        classification=classification,
        sources=[],
    )

    return Answer(text=text, structured=structured, confidence=0.9, meta={"intent": intent_id})
