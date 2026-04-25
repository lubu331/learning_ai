from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "student"

class LoginRequest(BaseModel):
    username: str
    password: str

class QuizResponse(BaseModel):
    id: int
    title: str
    topic: str
    grade_level: str
    questions_json: str