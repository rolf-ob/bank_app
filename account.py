from sqlalchemy import ForeignKey, String, Numeric, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from sqlalchemy.exc import IntegrityError

from user import Base

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="accounts")

    name: Mapped[str] = mapped_column(String(255))
    balance: Mapped[int] = mapped_column(Numeric(precision=12, scale=12))

def create_account(engine, user, name):
    with Session(engine) as session:
        try:
            account = Account(
                user=user,
                name=name,
                balance=0
            )

            session.add(account)
            session.commit()
            return account
        
        except IntegrityError:
            session.rollback()
            return None

def get_user_accounts(engine, user):
    with Session(engine) as session:
        statement = select(Account).where(Account.user_id == user.id)
        accounts = session.scalars(statement).all()

        return accounts