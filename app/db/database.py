from sqlmodel import SQLModel, create_engine, Field, Session, select, Relationship, col
from fastapi import Depends
from enum import Enum
import os

DATABASE_URL = "sqlite:///app/db/data.db"

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

def get_session():
    with Session(engine) as session:
        yield session

# =============== USER ===============

def create_database_and_tables(session: Session, passwd: str):
    SQLModel.metadata.create_all(engine)
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


def insert_user(session: Session, user):
    session.add(user)
    try:
        session.commit()
    except Exception:
        raise ValueError
    session.refresh(user)


def get_users(session: Session) -> list[UserDB]:
    users = session.exec(select(UserDB)).all()
    return users


def get_user_by_username(session: Session, username: str) -> UserDB | None:
    user = session.exec(select(UserDB).where(UserDB.username == username)).first()
    return user


def get_user_by_id(session: Session, id: int) -> UserDB | None:
    user = session.get(UserDB, id)
    return user


def remove_user_by_id(session: Session, id: int):
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

    user_cards: list["UserCardDB"] = Relationship(back_populates="card")


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


def insert_card(session: Session, card):
    session.add(card)
    try:
        session.commit()
    except Exception:
        raise ValueError
    session.refresh(card)


def get_cards(session: Session) -> list[CardDB]:
    cards = session.exec(select(CardDB)).all()
    return cards


def get_card_by_name(session: Session, name: str) -> CardDB | None:
    card = session.exec(select(CardDB).where(CardDB.name == name)).first()
    return card


def get_card_by_id(session: Session, id: int) -> CardDB | None:
    card = session.get(CardDB, id)
    return card


def get_cards_by_expansion(session: Session, id_expansion: int) -> list[CardDB]:
    cards = session.exec(select(CardDB).where(CardDB.id_expansion == id_expansion)).all()
    return cards


def get_cards_by_expansion_and_rarity(session: Session, id_expansion: int, rarity: Rarity) -> list[CardDB]:
    cards = session.exec(select(CardDB).where(CardDB.id_expansion == id_expansion).where(CardDB.rarity == rarity.value)).all()
    return cards


# =============== EXPANSION ===============
class ExpansionDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_generation: int = Field(index=True)
    name: str = Field(index=True)
    year: int = Field(index=True)


def insert_expansion(session: Session, expansion):
    session.add(expansion)
    try:
        session.commit()
    except Exception:
        raise ValueError
    session.refresh(expansion)


def get_expansion_by_name(session: Session, name: str) -> ExpansionDB | None:
    card = session.exec(select(ExpansionDB).where(ExpansionDB.name == name)).first()
    return card


def get_expansion_by_id(session: Session, id: int) -> ExpansionDB | None:
    card = session.get(ExpansionDB, id)
    return card


def get_expansions(session: Session) -> list[ExpansionDB]:
    cards = session.exec(select(ExpansionDB)).all()
    return cards


# =============== GENERATION ===============
class GenerationDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    year: int = Field(index=True)


def insert_generation(session: Session, generations):
    session.add(generations)
    try:
        session.commit()
    except Exception:
        raise ValueError
    session.refresh(generations)


def get_generation_by_name(session: Session, name: str) -> GenerationDB | None:
    card = session.exec(select(GenerationDB).where(GenerationDB.name == name)).first()
    return card


def get_generation_by_id(session: Session, id: int) -> GenerationDB | None:
    card = session.get(GenerationDB, id)
    return card


def get_generations(session: Session) -> list[GenerationDB]:
    cards = session.exec(select(GenerationDB)).all()
    return cards


# =============== USER_CARD ===============
class UserCardDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
#    id_card: int = Field(index=True)
    id_user: int = Field(index=True)
    price: float = Field(index=True)
    psa: int | None = Field(index=True)
    sold: bool = Field(index=True, default=True)

    id_card: int = Field(default=None, foreign_key="carddb.id")
    card: CardDB | None = Relationship(back_populates="user_cards")


def create_user_card(session: Session, user_card) -> None:
    session.add(user_card)
    try:
        session.commit()
    except Exception:
        raise ValueError
    session.refresh(user_card)


def get_user_cards(session: Session, id_user: int, offset: int, limit: int) -> list[UserCardDB]:
    user_cards = session.exec(select(UserCardDB).where(UserCardDB.id_user == id_user).offset(offset).limit(limit)).all()
    id_cards: set = set([card.id_card for card in user_cards])
    cards = session.exec(select(CardDB).where(col(CardDB.id).in_(list(id_cards)))).all()
    return [user_cards, cards]


def get_user_cards_by_expansion(session: Session, id_user: int, id_expansion: int, limit: int, offset: int):
    statement = select(UserCardDB).join(CardDB, UserCardDB.id_card == CardDB.id)
    statement = statement.where(UserCardDB.id_user == id_user).where(CardDB.id_expansion == id_expansion)
    statement = statement.offset(offset).limit(limit)
    user_cards = session.exec(statement).all()
    id_cards: set = set([card.id_card for card in user_cards])
    cards = session.exec(select(CardDB).where(col(CardDB.id).in_(list(id_cards)))).all()
    return [user_cards, cards]


def get_user_progression(session: Session, id: int, id_expansion: int) -> dict[CardDB, UserCardDB]:
    statement = select(UserCardDB)

# TODO: terminar los que quedan
# =============== TRANSACTION ===============



# =============== TRADE ===============

