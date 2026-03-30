from sqlalchemy.orm import Session
from app.models.user import User


class UsersService:

    @staticmethod
    def list_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()
