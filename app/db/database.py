from sqlmodel import SQLModel, create_engine, Field, Session, select
import os

DATABASE_URL = "sqlite:///app/db/data.db"

class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str = Field(index=True)  
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    money: float | None = Field(default=0.0, index=True)
    address: str | None = Field(default=None, index=True)
    exchanges: int | None = Field(default=0, index=True)
    

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


def create_database_and_tables():
    SQLModel.metadata.create_all(engine)


def insert_user(user):
    with Session(engine) as session:
        session.add(user)
        try:
            session.commit()
        except Exception:
            raise ValueError
        session.refresh(user)


def get_users() -> list[UserDB]:
    with Session(engine) as session:
        users = session.exec(select(UserDB)).all()
        return users


def get_user_by_username(username: str) -> UserDB | None:
    with Session(engine) as session:
        users = session.exec(select(UserDB).where(UserDB.username == username)).first()
        return users


# =============== CARD ===============

class CardDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_expansion: int = Field(index=True)
    name: str = Field(index=True)
    rarity: str = Field(index=True)
    frontcard: str = Field(index=True)
    backcard: str = Field(index=True)


def insert_card(card):
    with Session(engine) as session:
        session.add(card)
        try:
            session.commit()
        except Exception:
            raise ValueError
        session.refresh(card)


def get_cards() -> list[CardDB]:
    with Session(engine) as session:
        cards = session.exec(select(CardDB)).all()
        return cards


def get_card_by_name(name: str) -> CardDB | None:
    with Session(engine) as session:
        card = session.exec(select(CardDB).where(CardDB.name == name)).first()
        return card

# =============== EXPANSION ===============
class ExpansionDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_generation: int = Field(index=True)
    name: str = Field(index=True)
    year: int = Field(index=True)


def insert_expansion(expansion):
    with Session(engine) as session:
        session.add(expansion)
        try:
            session.commit()
        except Exception:
            raise ValueError
        session.refresh(expansion)


def get_expansion_by_name(name: str) -> ExpansionDB | None:
    with Session(engine) as session:
        card = session.exec(select(ExpansionDB).where(ExpansionDB.name == name)).first()
        return card


def get_expansions() -> list[ExpansionDB]:
    with Session(engine) as session:
        cards = session.exec(select(ExpansionDB)).all()
        return cards


# =============== GENERATION ===============
class GenerationDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    year: int = Field(index=True)


def insert_generation(generations):
    with Session(engine) as session:
        session.add(generations)
        try:
            session.commit()
        except Exception:
            raise ValueError
        session.refresh(generations)


def get_generation_by_name(name: str) -> GenerationDB | None:
    with Session(engine) as session:
        card = session.exec(select(GenerationDB).where(GenerationDB.name == name)).first()
        return card


def get_generations() -> list[GenerationDB]:
    with Session(engine) as session:
        cards = session.exec(select(GenerationDB)).all()
        return cards


# TODO: terminar los que quedan
# =============== USER_CARD ===============



# =============== TRANSACTION ===============



# =============== TRADE ===============



