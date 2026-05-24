from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.repositories.user import UserRepository
from app.services.auth import hash_password, verify_password, create_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str
    password: str
    role: str = "counselor"
    college: str = ""


class LoginRequest(BaseModel):
    name: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict


@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if len(req.name) < 2:
        raise HTTPException(status_code=400, detail="用户名至少2个字符")
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="密码至少4个字符")

    repo = UserRepository(db)
    existing = repo.get_by_name(req.name)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = repo.create(
        name=req.name,
        password_hash=hash_password(req.password),
        role=req.role,
        college=req.college,
    )
    token = create_token(user.id, user.name, user.role)
    return {"token": token, "user": {"id": user.id, "name": user.name, "role": user.role, "college": user.college}}


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_name(req.name)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user.id, user.name, user.role)
    return {"token": token, "user": {"id": user.id, "name": user.name, "role": user.role, "college": user.college}}


@router.get("/me")
def me(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    payload = decode_token(authorization[7:])
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期")
    user = UserRepository(db).get_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return {"id": user.id, "name": user.name, "role": user.role, "college": user.college}
