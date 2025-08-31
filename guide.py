from typing import Optional, Dict, Any, List
import os, yaml
from utils import normalize

CFG_PATH = os.path.join("schemas", "guide.yaml")
GUIDE = None

def load() -> dict:
    global GUIDE
    if GUIDE is None:
        if os.path.exists(CFG_PATH):
            with open(CFG_PATH, "r", encoding="utf-8") as f:
                GUIDE = yaml.safe_load(f) or {}
        else:
            GUIDE = {"topics": []}
        for t in GUIDE.get("topics", []) or []:
            t["id_norm"] = normalize(t.get("id", ""))
            syns = t.get("synonyms", []) or []
            t["syn_norm"] = [normalize(s) for s in syns]
    return GUIDE

def classify_topic(text: str) -> Optional[str]:
    cfg = load()
    q = normalize(text or "")
    best_id: Optional[str] = None
    best_score = 0
    for t in cfg.get("topics", []) or []:
        idn = t.get("id_norm") or ""
        if idn and idn in q:
            sc = len(idn)
            if sc > best_score:
                best_id, best_score = t.get("id"), sc
        for syn in t.get("syn_norm") or []:
            if syn and syn in q:
                sc = len(syn)
                if sc > best_score:
                    best_id, best_score = t.get("id"), sc
    return best_id

def get_guide(topic_id: str) -> Optional[Dict[str, Any]]:
    cfg = load()
    for t in cfg.get("topics", []) or []:
        if t.get("id") == topic_id:
            return {"id": t.get("id"), "title": t.get("title"), "steps": t.get("steps", [])}
    return None
