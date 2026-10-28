import jwt

from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from sqlalchemy import String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

hasher = PasswordHasher()

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

def create_user(engine, email, password):
    with Session(engine) as session:
        try:
            user = User(
                name=email.split("@")[0],
                email=email,
                password_hash=hasher.hash(password)
            )
            session.add(user)
            session.commit()
        
        except IntegrityError:
            session.rollback()
            return None

        return user

def login_user(engine, email, password):
    user = get_user_by_email(engine, email)

    if user and verify_password(user.password_hash, password):
        return user
    
    return None

def get_user_by_email(engine, email):
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.scalar(statement)

        return user

def verify_password(stored_hash, password):
    try:
        hasher.verify(stored_hash, password)
        return True
    
    except VerifyMismatchError:
        return False

def create_jwt_token(secret_key, user_id):
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {
        "sub": str(user_id),
        "exp": expires_at.timestamp()
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")

def get_user_by_token(engine, secret_key, token):
    with Session(engine) as session:
        payload = verify_token(secret_key, token)

        if payload and "sub" in payload:
            try:
                user_id = int(payload["sub"])
            except (ValueError, TypeError):
                return None
        else:
            return None

        statement = select(User).where(User.id == user_id)
        user = session.scalar(statement)

        return user

def verify_token(secret_key, token):
    try:
        return jwt.decode(token, secret_key, algorithms=["HS256"])

    except jwt.exceptions.InvalidTokenError:
        return None