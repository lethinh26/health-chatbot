from typing import Any, Dict, List, Tuple, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://api-gateway.whodev.top/patients/health-records/patient/{patient_id}"

# maintain

# def session_retry(total: int = 3, backoff: float = 0.3) -> requests.Session:
#     session = requests.Session()
#     retry = Retry(total=total, backoff_factor=backoff, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST"])
#     adapter = HTTPAdapter(max_retries=retry)
#     session.mount("https://", adapter)
#     return session


def parse_bp(bp: str) -> Tuple[Optional[int], Optional[int]]:
    """Tinh sbp dbp"""
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

def build_profile_api(patient_id: str, token: str) -> tuple[list, dict]: # update retries and timeout
    """Lấy data từ API xét nghiệm"""
    if not token or not patient_id:
        raise PermissionError("Thiếu token hoặc Patient-Id")

    headers = {
        "Authorization": token if token.lower().startswith("bearer ") else f"Bearer {token}"
    }

    # replace session_retry
    url = API_URL.format(patient_id=patient_id)
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount("https://", adapter)
    resp = session.get(url, headers=headers, timeout=10)

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
