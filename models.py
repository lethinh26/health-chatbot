from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class NumberItem(BaseModel):
    name: str
    value: Any = None
    unit: Optional[str] = None
    date: Optional[str] = None

class AnswerStructured(BaseModel):
    conclusion: Optional[str] = None
    numbers: List[NumberItem] = []
    trend: Optional[Any] = None
    targets: List[str] = []
    actions: List[str] = []
    cautions: List[str] = []
    classification: Dict[str, Any] = {}
    sources: List[str] = []

class Answer(BaseModel):
    text: str
    structured: AnswerStructured
    confidence: float = 0.9
    meta: Dict[str, Any] = {}

class ApiResponse(BaseModel):
    ok: bool
    data: Optional[Answer] = None
    error: Optional[Dict[str, Any]] = None
