from typing import Dict, Tuple
import os, yaml
from utils import normalize, contains_any
from guide import classify_topic
from tools import metrics_synonyms, lifestyle_config

def load_routerCFG() -> dict:
    path = os.path.join("schemas", "router.yaml")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

CFG = load_routerCFG()

def norm_list(xs) -> list[str]:
    return [normalize(str(x)) for x in (xs or [])]

# fixed BMI classify
BMI_CLASSIFY_KEYS = norm_list(CFG.get("bmi_classification_keywords"))
GREETING_SET = set(norm_list(CFG.get("greeting_synonyms")))
LAB_SUMMARY_SYNS = norm_list(CFG.get("lab_summary_synonyms"))

def is_greeting_only(q: str) -> bool:
    qn = normalize(q or "")
    qn = " ".join(qn.split())
    return qn in GREETING_SET

def detect_intent(question: str) -> Tuple[str, Dict]:
    qn = normalize(question or "")

    # greeting
    if is_greeting_only(qn):
        return "greet.smalltalk", {}

    # summary > guide
    if contains_any(qn, LAB_SUMMARY_SYNS):
        return "labs.summary", {}

    # guide
    topic_id = classify_topic(qn)
    if topic_id:
        return "guide.query", {"topic_id": topic_id}

    # fix catch bmi
    if contains_any(qn, BMI_CLASSIFY_KEYS):
        return "vital.query", {"metric": "bmi", "query_kind": "classification"}

    # metric
    syn = metrics_synonyms()
    for metric_id, kw_list in syn.items():
        kw_norm = norm_list(kw_list)
        if contains_any(qn, kw_norm):
            kind = "classification" if (metric_id == "bmi" and contains_any(qn, BMI_CLASSIFY_KEYS)) else "value"
            return "vital.query", {"metric": metric_id, "query_kind": kind}

    # lifestyle
    ls = lifestyle_config()
    ls_syn = norm_list(ls.get("synonyms", []))
    if contains_any(qn, ls_syn):
        return "lifestyle.advice", {}

    # fallback
    return "fallback.clarify", {}
