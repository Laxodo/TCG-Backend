from sqlmodel import SQLModel, create_engine, Field, Session, select
import os

DATABASE_URL = "sqlite///data.db"


class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str = Field(index=True)  
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    money: float | None = Field(default=0.0, index=True)
    address: str | None = Field(default=None, index=True)
    exanges: int | None = Field(default=0, index=True)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

def create_database_and_tables():
    SQLModel.metadata.create_all(engine)

def insert_user(user):
    with Session(engine) as session:
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            raise ValueError
        session.refresh(user)

def get_users() -> list[UserDB]:
    with Session(engine) as session:
        users = session.exec(select(UserDB)).all()
        return users

def get_user_by_username(username: str) -> UserDB:
    with Session(engine) as session:
        users = session.exec(select(UserDB)).where(UserDB.id == username).first()
        return users


def insert_card(card):
    with Session(engine) as session:
        session.add(card)
        try:
            session.commit()
        except IntegrityError:
            raise ValueError
        session.refresh(card)

def get_cards() -> list[CardDB]:
    with Session(engine) as session:
        cards = session.exec(select(CardDB)).all()
        return cards

def get_card(id: int) -> CardDB:
    with Session(engine) as session:
        card = session.exec(select(CardDB)).where(CardDB.id == id).first()
        return card
