from unidecode import unidecode

def normalize(text: str) -> str:
    return unidecode((text or "")).lower().strip()

def contains_any(text: str, keywords: list[str]) -> bool:
    if text is None:
        return False
    q = normalize(text)
    return any((normalize(k) in q) for k in keywords if k)