from typing import Dict, Any, List
from models import Answer, AnswerStructured, NumberItem

def join_numbers(nums: List[dict]) -> str:
    lines: List[str] = []
    for n in nums:
        s = f"- {n.get('name')}: {n.get('value')}{(' ' + n.get('unit')) if n.get('unit') else ''}"
        if n.get('date'):
            s += f" ({n.get('date')})"
        lines.append(s)
    return "\n".join(lines)

def render_items(items: List[dict]) -> str:
    lines: List[str] = []
    for it in items:
        title = it.get("title") or it.get("metric")
        val = it.get("value")
        unit = it.get("unit") or ""
        label = it.get("label")
        status = it.get("status")
        advice_top = it.get("advice_top")
        badge = "Tốt" if status == "good" else "Chưa tốt"
        val_part = f": {val} {unit}".strip() if val is not None else ""
        line = f"- {title}{val_part} — Trạng thái: {badge}"
        if label:
            line += f" ({label})"
        if advice_top:
            line += f". Lời khuyên: {advice_top}"
        lines.append(line)
    return "\n".join(lines)

def compose(intent_id: str, payload: Dict[str, Any]) -> Answer:
    explanations: List[str] = payload.get("explanations", [])
    numbers: List[dict] = payload.get("numbers", [])
    actions: List[str] = payload.get("actions", [])
    cautions: List[str] = payload.get("cautions", [])
    classification: Dict[str, Any] = payload.get("classification", {})
    # add sugg
    suggestions: List[str] = payload.get("suggestions", [])
    targets: List[str] = payload.get("targets", []) or suggestions

    # nodata
    if payload.get("no_data") is True:
        blocks: List[str] = []
        conclusion = explanations[0] if explanations else "Xin lỗi, tôi chưa biết trả lời câu này."
        blocks.append(conclusion)
        if targets:
            blocks.append("Hướng dẫn sử dụng:\n" + "\n".join([f"- {t}" for t in targets]))
        if actions:
            blocks.append("Bạn nên:\n" + "\n".join([f"- {a}" for a in actions]))
        if cautions:
            blocks.append("Lưu ý:\n" + "\n".join([f"- {c}" for c in cautions]))
        text = "\n\n".join(blocks).strip()

        structured = AnswerStructured(
            conclusion=conclusion,
            numbers=[],
            targets=targets,                # add target
            actions=actions,
            cautions=cautions,
            classification=classification,
        )
        return Answer(text=text, structured=structured, confidence=payload.get("confidence", 0.6), meta={"intent": intent_id})

    # normal
    blocks: List[str] = []
    if explanations:
        blocks.append(explanations[0])
    if numbers:
        blocks.append("Chỉ số:\n" + join_numbers(numbers))
    items = classification.get("items") if isinstance(classification, dict) else None
    if items:
        blocks.append("Tổng hợp theo chỉ số:\n" + render_items(items))
    if targets:
        blocks.append("Hướng dẫn sử dụng:\n" + "\n".join([f"- {t}" for t in targets]))
    if actions:
        blocks.append("Bạn nên:\n" + "\n".join([f"- {a}" for a in actions]))
    if cautions:
        blocks.append("Lưu ý:\n" + "\n".join([f"- {c}" for c in cautions]))

    text = "\n\n".join(blocks).strip()

    structured = AnswerStructured(
        conclusion=explanations[0] if explanations else None,
        numbers=[NumberItem(**n) for n in numbers],
        targets=targets,                    # tagert
        actions=actions,
        cautions=cautions,
        classification=classification,
    )

    return Answer(text=text, structured=structured, confidence=payload.get("confidence", 0.9), meta={"intent": intent_id})
