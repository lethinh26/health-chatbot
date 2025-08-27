from typing import Dict, List, Tuple, Optional
import yaml, os

def load_advice() -> dict:
    # optimize chưa tối ưu
    path = os.path.join("schemas", "health_check_advice_vi.yml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def get(obj: dict, path: str):
    """Lấy ra giá trị cần trong kqxm"""
    # print(obj)
    # print(path)
    if not path:
        return None
    def traverse(root: dict, p: str):
        cur = root
        for part in p.split("."):
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        return cur

    val = traverse(obj, path)
    if val is not None:
        return val

    # print(val)
    if not path.startswith("latest."):
        val = traverse(obj, "latest." + path)
    # print(val)
    return val

def parse_range(value: float, expr: str) -> bool:
    """ktra 3 đk (x-y), (<=x || <x), (>=x || >y)"""
    expr = (expr or "").strip().replace(" ", "")
    try:
        if "-" in expr and not any(op in expr for op in ("<", ">", "<=", ">=")):
            a_str, b_str = expr.split("-", 1)
            return float(a_str) <= value <= float(b_str)
        if expr.startswith("<="): return value <= float(expr[2:])
        if expr.startswith(">="): return value >= float(expr[2:])
        if expr.startswith("<"):  return value <  float(expr[1:])
        if expr.startswith(">"):  return value >  float(expr[1:])
    except Exception:
        return False
    return False

def eval_logic_ascii(expr: str, ctx: dict) -> bool:
    """So sánh các rule"""
    if not expr:
        return False
    s = expr.replace(" ", "")

    tokens: List[str] = []
    i = 0
    while i < len(s):
        # optimize chưa tối  (xử lí quá rườm rà)
        if s[i:i+3].upper() == "AND":
            tokens.append("AND"); i += 3; continue
        if s[i:i+2].upper() == "OR":
            tokens.append("OR"); i += 2; continue
        tokens.append(s[i]); i += 1

    joined = []
    # print(tokens)
    buf = ""
    for t in tokens:
        if t in ("AND", "OR"):
            if buf: joined.append(buf); buf=""
            joined.append(t)
        else:
            buf += t
    if buf: joined.append(buf)

    def atom(a: str) -> bool:
        e = a
        for k, v in ctx.items():
            if v is None: return False
            e = e.replace(k, str(v))

        for op in ("<=", ">=", "<", ">"):
            if op in e:
                L, R = e.split(op, 1)
                try:
                    Lf = float(L)
                    Rf = float(R)
                except Exception:
                    return False
                if op == "<":  return Lf < Rf
                if op == ">":  return Lf > Rf
                if op == "<=": return Lf <= Rf
                if op == ">=": return Lf >= Rf
        return False

    val: Optional[bool] = None
    op: Optional[str] = None
    for token in joined:
        if token in ("AND", "OR"):
            op = token
            continue
        res = atom(token)
        if val is None:
            val = res
        else:
            val = (val and res) if op == "AND" else (val or res)
    return bool(val)

def format_number(profile: dict, number_cfg: dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Định dạng giá trị (189 cm 2025)"""
    if not number_cfg:
        return None, None, None
    unit = number_cfg.get("unit")
    date = get(profile, number_cfg.get("date_from"))
    tpl = number_cfg.get("template")
    if tpl:
        variables = number_cfg.get("variables", {}) or {}
        values = {}
        for var, path in variables.items():
            values[var] = get(profile, path)
        try:
            val = tpl.format(**values)
        except Exception:
            val = None
        return val, unit, date
    else:
        path = number_cfg.get("value_from")
        val = get(profile, path)
        # print(val, unit, date)
        return val, unit, date

def classify_with_ranges(value: float, metric_cfg: dict):
    #note
    cats = metric_cfg.get("categories", []) or []
    for c in cats:
        rng = c.get("range")
        if rng and parse_range(value, rng):
            adv = metric_cfg.get("advice", {}) or {}
            tips = (adv.get("general", []) or []) + (adv.get("by_category", {}).get(c.get("id"), []) or [])
            cautions = metric_cfg.get("cautions", []) or []
            return c, tips, cautions
    adv = metric_cfg.get("advice", {}) or {}
    return None, (adv.get("general", []) or []), (metric_cfg.get("cautions", []) or [])

def classify(ctx: dict, metric_cfg: dict):
    #note
    cats = metric_cfg.get("categories", []) or []
    for c in cats:
        rule = c.get("rule")
        if rule and eval_logic_ascii(rule, ctx):
            adv = metric_cfg.get("advice", {}) or {}
            tips = (adv.get("general", []) or []) + (adv.get("by_category", {}).get(c.get("id"), []) or [])
            cautions = metric_cfg.get("cautions", []) or []
            return c, tips, cautions
    adv = metric_cfg.get("advice", {}) or {}
    return None, (adv.get("general", []) or []), (metric_cfg.get("cautions", []) or [])

def advice_for_metric(metric_id: str, profile: dict) -> dict:
    """object lời khuyên + cautions"""
    #note
    cfg = load_advice()
    metrics = cfg.get("metrics", [])
    metric_cfg = next((m for m in metrics if m.get("id") == metric_id), None)
    if not metric_cfg:
        return {"label": None, "tips": [], "cautions": [], "number": (None, None, None), "title": metric_id}

    number_val, number_unit, number_date = format_number(profile, metric_cfg.get("number"))
    kind = (metric_cfg.get("kind") or "range").lower()
    label = None
    tips: List[str] = []
    cautions: List[str] = []

    if kind == "range":
        val_path = metric_cfg.get("number", {}).get("value_from")
        value = get(profile, val_path) if val_path else None
        if isinstance(value, (int, float)):
            cat, tips, cautions = classify_with_ranges(float(value), metric_cfg)
            label = cat.get("label") if cat else None
        else:
            adv = metric_cfg.get("advice", {}) or {}
            tips = adv.get("general", []) or []
            cautions = metric_cfg.get("cautions", []) or []

    elif kind == "logic":
        variables = metric_cfg.get("variables", {}) or {}
        ctx = {var: get(profile, path) for var, path in variables.items()}
        cat, tips, cautions = classify(ctx, metric_cfg)
        label = cat.get("label") if cat else None

    else:
        adv = metric_cfg.get("advice", {}) or {}
        tips = adv.get("general", []) or []
        cautions = metric_cfg.get("cautions", []) or []

    return {
        "metric": metric_id,
        "label": label,
        "tips": tips,
        "cautions": cautions,
        "number": (number_val, number_unit, number_date),
        "title": metric_cfg.get("title"),
    }

def metrics_synonyms() -> Dict[str, List[str]]:
    """Map metric"""
    cfg = load_advice()
    out: Dict[str, List[str]] = {}
    for m in cfg.get("metrics", []):
        out[m.get("id")] = [str(s) for s in (m.get("synonyms") or [])]
    return out

def lifestyle_config() -> dict:
    """Map lifestyle"""
    cfg = load_advice()
    ls = cfg.get("lifestyle", {}) or {}
    return {
        "synonyms": [str(s) for s in (ls.get("synonyms") or [])],
        "diet_general": ls.get("diet_general", []),
        "physical_activity": ls.get("physical_activity", []),
        "general_warnings": ls.get("general_warnings", []),
    }
