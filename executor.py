from guide import get_guide
from typing import Any, Dict, List
# from utils import normalize
import re
from tools import advice_for_metric, lifestyle_config, metrics_synonyms

def execute(intent_id: str, slots: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    # smalltalk suggest
    if intent_id == "greet.smalltalk":
        text = "Xin chào! Mình có thể giúp bạn đọc kết quả xét nghiệm, xem chỉ số (BMI, huyết áp, đường huyết…), hoặc hướng dẫn sử dụng hệ thống."
        suggestions = [
            "tổng hợp lời khuyên từ xét nghiệm của tôi",
            "BMI của tôi",
            "Huyết áp của tôi",
            "Hướng dẫn tôi đăng ký"
        ]
        explanations = [text]
        return {
            "no_data": False,
            "explanations": explanations,
            "targets": [f"Hỏi: “{s}”" for s in suggestions]
        }

    # summary metric
    if intent_id == "labs.summary":
        syn = metrics_synonyms()
        metrics = list(syn.keys())
        numbers = []
        actions: List[str] = []
        cautions: List[str] = []
        explanations: List[str] = ["Tổng hợp lời khuyên về xét nghiệm"]
        items: List[Dict[str, Any]] = []

        NORMAL_IDS = {"normal", "optimal", "good", "target"}
        NORMAL_LABELS = {"bình thường", "binh thuong", "normal", "tối ưu", "toi uu", "optimal"}

        for mid in metrics:
            info = advice_for_metric(mid, profile)
            title = info.get("title") or mid
            val, unit, date = info.get("number", (None, None, None))
            label = (info.get("label") or "") or None
            cat_id = (info.get("category_id") or "") or None

            actions.extend(info.get("tips") or [])
            cautions.extend(info.get("cautions") or [])

            status = None
            if label or cat_id or val is not None:
                if (cat_id and str(cat_id).lower() in NORMAL_IDS) or (label and str(label).lower() in NORMAL_LABELS):
                    status = "good"
                else:
                    status = "not_good"

            first_tip = (info.get("tips") or [None])[0]
            if status:
                items.append({
                    "metric": mid,
                    "title": title,
                    "value": val,
                    "unit": unit,
                    "date": date,
                    "status": status,
                    "label": label,
                    "advice_top": first_tip,
                })

            if val is not None:
                numbers.append({"name": title, "value": val, "unit": unit, "date": date})

        
        items.sort(key=lambda x: 0 if x.get("status") == "not_good" else 1)
        # print(items)

        # de-dup
        def _dedup(seq):
            seen = set(); out = []
            for x in seq:
                if x and x not in seen:
                    out.append(x); seen.add(x)
            return out

        actions = _dedup(actions)[:10]
        cautions = _dedup(cautions)[:6]

        if not items and not actions and not cautions:
            ls = lifestyle_config()
            actions = _dedup((ls.get("diet_general") or []) + (ls.get("physical_activity") or []))[:8]
            cautions = _dedup(ls.get("general_warnings") or [])[:5]

        return {
            "no_data": False,
            "numbers": numbers,
            "classification": {"items": items},
            "actions": actions,
            "cautions": cautions,
            "explanations": explanations,
        }

    # vital
    if intent_id == "vital.query":
        metric = (slots or {}).get("metric")
        kind = (slots or {}).get("query_kind") or "value"
        if not metric:
            syn = metrics_synonyms()
            q = (slots or {}).get("q") or ""
            for mid, kws in syn.items():
                if any((k.lower() in q.lower()) for k in (kws or [])):
                    metric = mid; break
        if not metric:
            return {"no_data": True, "explanations": ["Xin lỗi, mình chưa biết trả lời câu này."]}

        info = advice_for_metric(metric, profile)
        title = info.get("title") or metric
        val, unit, date = info.get("number", (None, None, None))
        label = info.get("label")
        cat_id = info.get("category_id")

        actions: List[str] = (info.get("tips") or [])[:5]
        cautions: List[str] = (info.get("cautions") or [])[:5]

        if val is None and label is None:
            return {"no_data": True, "explanations": [f"Chưa tìm thấy dữ liệu cho {title}."]}

        msg = None
        if val is not None:
            msg = f"{title} gần nhất: {val}{(' ' + unit) if unit else ''}" + (f" (ngày {date})" if date else "")
            if kind == "classification" and label:
                msg += f". Phân loại: {label}."
        elif label:
            msg = f"{title}: {label}."
        explanations = [msg]

        numbers = []
        if val is not None:
            numbers = [{"name": title, "value": val, "unit": unit, "date": date}]

        classification = {}
        if label or cat_id:
            classification = {"label": label, "category_id": cat_id}

        return {
            "no_data": False,
            "numbers": numbers,
            "actions": actions,
            "cautions": cautions,
            "explanations": explanations,
            "classification": classification,
        }

    # guide topic 
    if intent_id == "guide.query":
        topic_id = (slots or {}).get("topic_id") or ""
        g = get_guide(topic_id)
        if not g:
            return {
                "no_data": True,
                "explanations": ["Xin lỗi, mình chưa tìm thấy chủ đề hướng dẫn phù hợp."],
            }
        items = [ { "title": g.get("title") or topic_id, "steps": g.get("steps") or [] } ]
        return {
            "no_data": False,
            "numbers": [],
            "actions": [],
            "cautions": [],
            "explanations": [f"Hướng dẫn: {g.get('title') or topic_id}"],
            "classification": {"items": items, "topic_id": g.get("id") or topic_id},
        }

    if intent_id == "fallback.clarify":
        return {
            "no_data": True,
            "explanations": ["Mình chưa rõ bạn muốn xem chỉ số nào. Bạn có thể chọn một trong các mục dưới đây:"],
            "suggestions": ["BMI của tôi", "Huyết áp của tôi", "Đường huyết của tôi", "Tổng hợp xét nghiệm"],
            "numbers": [],
            "actions": [],
            "cautions": [],
            "classification": {},
        }
