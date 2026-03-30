from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[EmailStr] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    role: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    pass
