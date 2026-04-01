from fastapi import APIRouter
from app.api.v1.controllers import user_controller

api_router = APIRouter()

# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(user_controller.router, prefix="/users", tags=["users"])
