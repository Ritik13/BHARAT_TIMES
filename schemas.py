from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    id: Optional[int] = None
    title: str = Field(... , min_length=3, max_length=100)
    content: str= Field(... , min_length=10)
    published: bool

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if value.strip() == "":
            raise ValueError("Title cannot be blank")
        return value.strip()


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool

    class Config:
        from_attributes= True



class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
