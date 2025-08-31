from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class NumberItem(BaseModel):
    name: str
    value: Any = None
    unit: Optional[str] = None
    date: Optional[str] = None

class AnswerStructured(BaseModel):
    # field tránh trùng dict
    conclusion: Optional[str] = None
    numbers: List[NumberItem] = Field(default_factory=list)
    trend: Optional[Any] = None
    targets: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    cautions: List[str] = Field(default_factory=list)
    classification: Dict[str, Any] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)

class Answer(BaseModel):
    text: str
    structured: AnswerStructured
    confidence: float = 0.9
    meta: Dict[str, Any] = {}

class ApiResponse(BaseModel):
    ok: bool
    data: Optional[Answer] = None
    error: Optional[Dict[str, Any]] = None
