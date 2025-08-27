from typing import Any, Dict, List, Tuple, Optional
import requests

API_URL = "https://api-gateway.whodev.top/patients/health-records/patient/{patient_id}"

def parse_bp(bp: str) -> Tuple[Optional[int], Optional[int]]:
    if not bp:
        return None, None
    try:
        parts = str(bp).split("/")
        if len(parts) != 2:
            return None, None
        sbp = int(parts[0].strip())
        dbp = int(parts[1].strip())
        return sbp, dbp
    except Exception:
        return None, None

def bmi(height_cm: Optional[float], weight_kg: Optional[float]) -> Optional[float]:
    if height_cm is None or weight_kg is None:
        return None
    h = float(height_cm) / 100.0
    if h <= 0:
        return None
    return round(float(weight_kg) / (h * h), 2)

def build_profile_api(patient_id: str, token: str) -> tuple[list, dict]:
    if not token or not patient_id:
        raise PermissionError("Thiếu token hoặc Patient-Id")

    headers = {
        "Authorization": token if token.lower().startswith("bearer ") else f"Bearer {token}"
    }
    url = API_URL.format(patient_id=patient_id)
    resp = requests.get(url, headers=headers, timeout=10)

    if resp.status_code == 401:
        raise PermissionError("AUTH_EXPIRED")
    if resp.status_code == 404:
        raise FileNotFoundError("PATIENT_NOT_FOUND")

    resp.raise_for_status()
    data = resp.json()

    if not isinstance(data, list):
        raise ValueError("UPSTREAM_BAD_FORMAT")

    normalized: List[Dict[str, Any]] = []

    for r in data:
        height_cm = r.get("heightInCm")
        weight_kg = r.get("weightInKg")
        sbp, dbp = parse_bp(r.get("bloodPressure"))

        vitals = {
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "bmi": bmi(height_cm, weight_kg),
            "sbp_mmHg": sbp,
            "dbp_mmHg": dbp,
            "hr_bpm": r.get("pulseRate"),
            "body_temp_c": r.get("bodyTemperature"),
            "measured_at": r.get("checkupDate"),
        }
        labs = {
            "glucose_mmol_l": r.get("bloodSugar"),
        }

        normalized.append({
            "vitals": vitals,
            "labs": labs,
            "raw": r,
        })

    latest = (
        sorted(normalized, key=lambda x: x["vitals"].get("measured_at") or "", reverse=True)[0]
        if normalized else {"vitals": {}, "labs": {}}
    )

    profile = {
        "latest": {
            "vitals": latest.get("vitals", {}),
            "labs": latest.get("labs", {}),
        },
        "history": normalized,
    }

    return data, profile
