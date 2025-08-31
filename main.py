from fastapi import FastAPI, Form, Header
from models import ApiResponse
from profiles import build_profile_api
from router import detect_intent
from executor import execute
from composer import compose

app = FastAPI(title="HMS")

@app.post("/ask")
async def ask(question: str = Form(...), authorization: str | None = Header(None, alias="Authorization"), patient_id: str | None = Header(None, alias="Patient-Id")):
    if not authorization or not patient_id:
        return ApiResponse(
            ok=False,
            error={"code": "BAD_REQUEST", "message": "Thiếu token hoặc patient id."}
        ).model_dump(exclude_none=True, exclude_defaults=True)

    try:
        #note thừa _
        _, profile = build_profile_api(patient_id, authorization)
    except PermissionError:
        return ApiResponse(ok=False, error={"code": "AUTH_EXPIRED", "message": "Phiên đăng nhập hết hạn."}).model_dump(exclude_none=True, exclude_defaults=True)
    except FileNotFoundError:
        return ApiResponse(ok=False, error={"code": "PATIENT_NOT_FOUND", "message": "Không tìm thấy hồ sơ."}).model_dump(exclude_none=True, exclude_defaults=True)
    except Exception as e:
        return ApiResponse(ok=False, error={"code": "UPSTREAM_UNAVAILABLE", "message": str(e)}).model_dump(exclude_none=True, exclude_defaults=True)

    profile["last_question"] = question

    intent_id, slots = detect_intent(question)
    payload = execute(intent_id, slots, profile)
    answer = compose(intent_id, payload)

    return ApiResponse(ok=True, data=answer).model_dump(exclude_none=True, exclude_defaults=True)
