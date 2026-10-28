"""Tầng 2 (lớp routes) - cổng HTTP của đăng nhập. Chỉ nhận yêu cầu, gọi service, trả kết quả."""
from fastapi import APIRouter, Body, Depends

from src.dependencies import current_user, get_auth_service
from src.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(body: dict = Body(...), auth: AuthService = Depends(get_auth_service)):
    return auth.login(body)


@router.get("/me")
def me(user=Depends(current_user)):
    return {"username": user["username"], "full_name": user["full_name"], "role": user["role"]}
