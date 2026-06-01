from sqlmodel import SQLModel, Field, Session, select, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserDB
    from .loghistory import LogHistoryDB
    from .logactivity import LogActivityDB
    from .cardmarket import CardMarketDB
    from .usercard import UserCardDB


class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    username: str = Field(index=True, unique=True)
    password: str = Field(index=True)  
    email: str = Field(index=True, unique=True)
    money: int = Field(default=0, index=True)
    opened_boosters: int = Field(default=0, index=True)
    exchanges: int | None = Field(default=0, index=True)
    is_admin: bool = Field(default=False, index=True)

    card_market: list["CardMarketDB"] = Relationship(back_populates="user")
    user_cards: list["UserCardDB"] = Relationship(back_populates="user")
    log_activity: list["LogActivityDB"] = Relationship(back_populates="user")
    log_history: list["LogHistoryDB"] = Relationship(back_populates="user", sa_relationship_kwargs={"foreign_keys": "LogHistoryDB.id_user"})
    log_history_interacted: list["LogHistoryDB"] = Relationship(back_populates="user_interacted", sa_relationship_kwargs={"foreign_keys": "LogHistoryDB.id_user_interacted"})


def insert_user(session: Session, user):
    session.add(user)


def get_users(session: Session) -> list[UserDB]:
    users = session.exec(select(UserDB)).all()
    return users


def get_user_by_username(session: Session, username: str) -> UserDB | None:
    user = session.exec(select(UserDB).where(UserDB.username == username)).first()
    return user


def get_user_by_email(session: Session, email: str) -> UserDB | None:
    user = session.exec(select(UserDB).where(UserDB.email == email)).first()
    return user


def get_user_by_id(session: Session, id: int) -> UserDB | None:
    user = session.get(UserDB, id)
    return user


def remove_user_by_id(session: Session, id: int):
    user = session.get(UserDB, id)
    if not user:
        return
    session.delete(user)


def update_user(
    session: Session, 
    id: int, 
    name: str | None = None, 
    username: str | None = None, 
    password: str | None = None,
    email: str | None = None,
    money: int | None = None,
    opened_boosters: int | None = None,
    exchanges: int | None = None,
    is_admin: bool | None = None
) -> UserDB:
    user = session.exec(select(UserDB).where(UserDB.id == id)).first()
    user.id = user.id if id is None else id
    user.name = user.name if name is None else name
    user.username = user.username if username is None else username
    user.password = user.password if password is None else password
    user.email = user.email if email is None else email
    user.money = user.money if money is None else money
    user.opened_boosters = user.opened_boosters if opened_boosters is None else opened_boosters
    user.exchanges = user.exchanges if exchanges is None else exchanges
    user.is_admin = user.is_admin if is_admin is None else is_admin

    session.add(user)
    return user