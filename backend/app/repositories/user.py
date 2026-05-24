from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_name(self, name: str):
        stmt = select(self.model).where(User.name == name)
        return self.db.scalars(stmt).first()
