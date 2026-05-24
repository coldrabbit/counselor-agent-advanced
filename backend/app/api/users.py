from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.repositories.user import UserRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(role: str | None = Query(None), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    if role:
        from app.models.user import User
        from sqlalchemy import select
        stmt = select(User).where(User.role == role).order_by(User.created_at.asc())
        return list(db.scalars(stmt).all())
    return list(repo.list_all())


@router.post("", response_model=UserResponse)
def create_user(req: UserCreate, db: Session = Depends(get_db)):
    existing = UserRepository(db).get_by_name(req.name)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    return UserRepository(db).create(name=req.name, role=req.role, college=req.college)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
