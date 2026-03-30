from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_admin
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.crud.user import user as crud_user
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(require_admin)
):
    """Get all users (admin only)"""
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user = Depends(require_admin)
):
    """Create new user (admin only)"""
    # Check if phone exists
    if crud_user.get_by_phone(db, phone=user_in.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Hash password before storing
    user_data = user_in.model_dump()
    user_data["password_hash"] = get_password_hash(user_data.pop("password"))
    
    # Create user with hashed password
    from app.models.user import User
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user = Depends(get_current_user)
):
    """Get current logged in user"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user by ID"""
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
