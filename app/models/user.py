from sqlalchemy import Column, String, Enum, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    # Fields will be updated based on final ER diagram
    role = Column(Enum("admin", "supervisor", "driver", name="user_roles"))
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # TODO: Add role-specific relationships after ER diagram is ready
