from sqlalchemy.orm import Session
from app.models.user import User


class UserService:

    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self):
        return self.db.query(User).all()

    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()
