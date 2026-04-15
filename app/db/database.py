from sqlmodel import SQLModel, create_engine, Field, Session, select
from enum import Enum
import os

DATABASE_URL = "sqlite:///app/db/data.db"
#DATABASE_URL = "sqlite:///app/db/testdata.db"

class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    username: str = Field(index=True, unique=True)
    password: str = Field(index=True)  
    email: str = Field(index=True, unique=True)
    money: float = Field(default=0.0, index=True)
    opened_boosters: int = Field(default=0, index=True)
    exchanges: int | None = Field(default=0, index=True)
    is_admin: bool = Field(default=False, index=True)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

# =============== USER ===============

def create_database_and_tables(passwd: str):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = UserDB(
                name = "admin",
                username = "admin",
                password = passwd,
                email = "admin@laxodo.com",
                money = 9999999,
                is_admin = True
            )
        try:
            session.add(user)
            session.commit()
            session.refresh()
        except Exception:
            pass


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
        user = session.exec(select(UserDB).where(UserDB.username == username)).first()
        return user


def get_user_by_id(id: int) -> UserDB | None:
    with Session(engine) as session:
        user = session.get(UserDB, id)
        return user


def remove_user_by_id(id: int):
    with Session(engine) as session:
        user = session.get(UserDB, id)
        if not user:
            return
        session.delete(user)
        session.commit()


# =============== CARD ===============

class CardDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_expansion: int = Field(index=True)
    name: str = Field(index=True)
    rarity: str = Field(index=True)
    price: float = Field(index=True)
    card_number: int = Field(index=True, unique=True)
    frontcard: str = Field(index=True)
    backcard: str = Field(index=True)


class Rarity(Enum):
    common = "Common"
    uncommon = "Uncommon"
    rare = "Rare"
    rare_holo = "Rare Holo"
    rainbow_rare = "Rainbow Rare"
    ultra_rare = "Ultra Rare"
    hyper_rare = "Hyper Rare"


rarity_variable: Enum = [Rarity.rare, Rarity.rare_holo, Rarity.rainbow_rare, Rarity.ultra_rare, Rarity.hyper_rare]
probabilities: list[int] = [70, 15, 10, 4, 1]


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


def get_card_by_id(id: int) -> CardDB | None:
    with Session(engine) as session:
        card = session.get(CardDB, id)
        return card


def get_cards_by_expansion(id_expansion: int) -> list[CardDB]:
    with Session(engine) as session:
        cards = session.exec(select(CardDB).where(CardDB.id_expansion == id_expansion)).all()
        return cards


def get_cards_by_expansion_and_rarity(id_expansion: int, rarity: Rarity) -> list[CardDB]:
    with Session(engine) as session:
        cards = session.exec(select(CardDB).where(CardDB.id_expansion == id_expansion).where(CardDB.rarity == rarity.value)).all()
        return cards


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


def get_expansion_by_id(id: int) -> ExpansionDB | None:
    with Session(engine) as session:
        card = session.get(ExpansionDB, id)
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


def get_generation_by_id(id: int) -> GenerationDB | None:
    with Session(engine) as session:
        card = session.get(GenerationDB, id)
        return card


def get_generations() -> list[GenerationDB]:
    with Session(engine) as session:
        cards = session.exec(select(GenerationDB)).all()
        return cards


# TODO: terminar los que quedan
# =============== USER_CARD ===============
class UserCardDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_card: int = Field(index=True)
    id_user: int = Field(index=True)
    price: float = Field(index=True)
    psa: int | None = Field(index=True)
    sold: bool = Field(index=True, default=True)


def create_user_card(user_card) -> None:
    with Session(engine) as session:
        session.add(user_card)
        try:
            session.commit()
        except Exception:
            raise ValueError
        session.refresh(user_card)


def get_user_cards(id_user: int) -> list[UserCardDB]:
    with Session(engine) as session:
        cards = session.exec(select(UserCardDB).where(UserCardDB.id_user == id_user)).all()
        return cards


def get_user_cards_by_expansion(id_user: int, id_expansion: int) -> list[UserCardDB]:
    with Session(engine) as session:
        cards = session.exec(select(UserCardDB, CardDB).where(UserCardDB.id_user == id_user).where(CardDB.id_expansion == id_expansion)).all()
        return cards

# =============== TRANSACTION ===============



# =============== TRADE ===============

