# app/core/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Any


# -------------------------
# USER SCHEMAS
# -------------------------

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# AUTH SCHEMAS
# -------------------------

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# -------------------------
# QUERY SCHEMAS
# -------------------------

class QueryBase(BaseModel):
    query_text: str
    result: Optional[str] = None


class QueryCreate(QueryBase):
    user_id: int


class QueryOut(QueryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# LOG SCHEMAS
# -------------------------

class LogBase(BaseModel):
    log_type: str
    message: str
    metadata: Optional[Any] = None


class LogCreate(LogBase):
    pass


class LogOut(LogBase):
    id: int
    log_time: datetime

    class Config:
        from_attributes = True
