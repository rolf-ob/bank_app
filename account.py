from decimal import Decimal

from sqlalchemy import ForeignKey, String, Numeric, select, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy.exc import IntegrityError

from user import Base

class Account(Base):
    __tablename__ = "accounts"

    __table_args__ = (
        UniqueConstraint("user_id", "name"),
    )

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
                balance=Decimal("0.00")
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

def get_user_account(engine, user, account_id):
    with Session(engine) as session:
        statement = select(Account).where(
            Account.user_id == user.id,
            Account.id == account_id
        )
        account = session.scalar(statement)
        return account