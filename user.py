import sqlalchemy

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from hashlib import sha256

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    password: Mapped[str] = mapped_column(String(200))

def create_user(engine, name, email, password):
    with Session(engine) as session:
        try:
            user = User(
                name=name,
                email=email,
                password=sha256(password.encode('utf-8')).hexdigest()
            )
            session.add(user)
            session.commit()

            return True
        
        except sqlalchemy.exc.IntegrityError:
            return False