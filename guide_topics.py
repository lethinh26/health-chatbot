from typing import Dict, Any, Optional, List
import yaml
import os
from unidecode import unidecode

YAML_PATH = os.path.join("schemas", "guide_topics.yaml")
CACHE: Dict[str, Any] | None = None

def normalize(text: str) -> str:
    return unidecode((text or "")).lower().strip()

def load() -> Dict[str, Any]:
    global CACHE
    if CACHE is None:
        with open(YAML_PATH, "r", encoding="utf-8") as f:
            CACHE = yaml.safe_load(f) or {}
    return CACHE

def classify_topic(user_query: str) -> Optional[str]:
    data = load()
    topics: List[Dict[str, Any]] = data.get("topics", [])
    qn = normalize(user_query)
    # print(qn)

    for t in topics:
        tid = t.get("id")
        for syn in t.get("synonyms", []):
            syn_n = normalize(syn)
            if syn_n and syn_n in qn:
                return tid
    return None

def topic_content(topic_id: str) -> Dict[str, Any]:
    data = load()
    for t in data.get("topics", []):
        if t.get("id") == topic_id:
            return t
    return {}
