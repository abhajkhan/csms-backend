from fastapi import APIRouter
from app.api.v1.controllers import users

api_router = APIRouter()

# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])


# TODO: Add more endpoints as they are developed
# api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
# api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
# api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
# api_router.include_router(warehouse.router, prefix="/warehouse", tags=["warehouse"])
