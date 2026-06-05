from app.db.models import CardDB
from sqlmodel import Session, select
from enum import Enum

class Rarity(Enum):
    common = "Common"
    uncommon = "Uncommon"
    rare = "Rare"
    rare_holo = "Rare Holo"
    rainbow_rare = "Rainbow Rare"
    ultra_rare = "Ultra Rare"
    hyper_rare = "Hyper Rare"


RARITY_VARIABLE: Enum = [Rarity.rare, Rarity.rare_holo, Rarity.rainbow_rare, Rarity.ultra_rare, Rarity.hyper_rare]
PROBABILITIES: list[int] = [70, 15, 10, 4, 1]


def insert_card(session: Session, card):
    session.add(card)


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
    