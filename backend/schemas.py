from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class QuestionCreate(BaseModel):
    type: str
    category: str
    content: str
    options: Optional[list] = None
    answer: str = ""
    explanation: str = ""
    difficulty: int = 1
    score: int = 2

class QuestionUpdate(BaseModel):
    type: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    options: Optional[list] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[int] = None
    score: Optional[int] = None

class ExamCreate(BaseModel):
    name: str
    type: str = "正式"
    duration: int = 60
    question_count: int = 30
    pass_score: int = 60
    strategy: str = "random"
    categories: Optional[list] = None
    distribution: Optional[dict] = None

class AnswerSubmit(BaseModel):
    questions: list
    answers: dict
    duration_used: int = 0
