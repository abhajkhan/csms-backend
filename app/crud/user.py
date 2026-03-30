from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_phone(self, db, phone: str):
        return db.query(User).filter(User.phone == phone).first()

    def get_by_email(self, db, email: str):
        return db.query(User).filter(User.email == email).first()


user = CRUDUser(User)
