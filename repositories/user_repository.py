# FILE: repositories/user_repository.py
from typing import Optional
from sqlalchemy.orm import Session
from models.user import User, Role


class UserRepository:

    def __init__(self, session: Session):
        self._session = session

    def get_by_username(self, username: str) -> Optional[User]:
        return (
            self._session.query(User)
            .filter(User.username == username)
            .first()
        )

    def get_all(self) -> list[User]:
        return self._session.query(User).order_by(User.full_name).all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._session.query(User).filter(User.id == user_id).first()

    def create(self, user: User) -> User:
        self._session.add(user)
        self._session.flush()
        return user

    def update(self, user: User) -> User:
        self._session.flush()
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            self._session.flush()
            return True
        return False