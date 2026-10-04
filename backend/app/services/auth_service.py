from sqlalchemy.orm import Session
from app.models.user import User
from app.security import create_access_token, hash_password, verify_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email.lower().strip()).first()

def create_user(db: Session, email: str, password: str):
    user = User(email=email.lower().strip(), password_hash=hash_password(password))
    db.add(user); db.commit(); db.refresh(user); return user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    return user if user and verify_password(password, user.password_hash) else None

def generate_token(user: User): return create_access_token(user.id)
