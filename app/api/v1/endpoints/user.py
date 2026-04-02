from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):

    user_service = UserService(db)
    user = user_service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
