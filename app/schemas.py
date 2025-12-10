from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# CHAT SCHEMAS
class ChatCreate(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    id: int
    prompt: str
    response: str
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class ErrorDetail(BaseModel):
    detail: str
    path: str
    method: str
    status: int
