import sqlalchemy

from sqlalchemy import String, select
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

def create_signin_user(engine, action, email, password):
    with Session(engine) as session:
        if action == "create account":
            try:
                user = User(
                    name=email.split("@")[0],
                    email=email,
                    password=sha256(password.encode("utf-8")).hexdigest()
                )
                session.add(user)
                session.commit()

                return ("account created", user.name)
            
            except sqlalchemy.exc.IntegrityError:
                return ("email taken", None)
        
        else:
            statement = select(User)
            users = session.scalars(statement).all()

            for user in users:
                if user.email == email:
                    if user.password == sha256(password.encode("utf-8")).hexdigest():
                        return ("logged in", user.name)
                    return ("incorrect password", None)
            return ("incorrect email", None)