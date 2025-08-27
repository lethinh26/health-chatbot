from typing import Dict, Tuple
from unidecode import unidecode
from guide_topics import classify_topic
from tools import metrics_synonyms, lifestyle_config

def normalize(text: str) -> str:
    return unidecode((text or "")).lower().strip()

BMI_KEY = [
    "gay", "gầy", "beo", "béo", "thua can", "thừa cân",
    "overweight", "underweight", "obese", "beo phi", "béo phì",
]

def contains_any(text: str, keywords: list[str]) -> bool:
    return any(k in text for k in keywords if k)

def detect_intent(question: str) -> Tuple[str, Dict]:
    qn = normalize(question)

    topic_id = classify_topic(question)
    if topic_id:
        return "guide.query", {"topic_id": topic_id}

    syn = metrics_synonyms()
    for metric_id, kw_list in syn.items():
        if contains_any(qn, kw_list):
            kind = "classification" if (metric_id == "bmi" and contains_any(qn, BMI_KEY)) else "value"
            return "vital.query", {"metric": metric_id, "query_kind": kind}

    ls = lifestyle_config()
    if contains_any(qn, ls.get("synonyms", [])):
        return "lifestyle.advice", {}

    return "greet.smalltalk", {}
