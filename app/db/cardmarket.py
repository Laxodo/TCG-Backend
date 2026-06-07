from app.db.models import CardMarketDB
from sqlmodel import Session, select
from enum import Enum

GRADE_COST: int = 2500

class ExchangeType(Enum):
    sale = "sell"
    exchange = "exchange"


def create_offer(session: Session, card: CardMarketDB) -> CardMarketDB:
    session.add(card)
    session.flush()
    return card


def remove_offer(session: Session, id: int) -> None:
    offer = session.get(CardMarketDB, id)
    session.delete(offer)


def get_offers(session: Session) -> list[CardMarketDB]:
    return session.exec(select(CardMarketDB)).all()


def get_offer_by_id(session: Session, id: int) -> CardMarketDB:
    return session.get(CardMarketDB, id)


def get_offers_by_user_id(session: Session, id_user: int, type: str | None = None) -> list[CardMarketDB]:
    statement = select(CardMarketDB).where(CardMarketDB.id_user == id_user)
    if type in [e.value for e in ExchangeType]:
        statement = statement.where(CardMarketDB.exchange_type == type)
    return session.exec(statement).all()


def get_offers_by_not_user_id(session: Session, id_user: int, type: str | None = None) -> list[CardMarketDB]:
    statement = select(CardMarketDB).where(CardMarketDB.id_user != id_user)
    if type in [e.value for e in ExchangeType]:
        statement = statement.where(CardMarketDB.exchange_type == type)
    return session.exec(statement).all()