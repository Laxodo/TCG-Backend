from sqlmodel import SQLModel, Field, Session, select, Relationship
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserDB
    from .card import CardDB
    from .cardmarket import CardMarketDB
    from .usercard import UserCardDB

    
# =============== MARKET ===============

class CardMarketDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_user: int = Field(index=True, foreign_key="userdb.id") # User that offers the card
    id_user_card: int = Field(index=True, foreign_key="usercarddb.id") # Offer card
    id_card: int | None = Field(index=True, foreign_key="carddb.id") # Demanded card
    psa: int | None = Field(default=None, index=True) # Demanded card psa

    exchange_type: str = Field(index=True) # For sale or exchange
    price: int | None = Field(default=None, index=True) # For sale price

    user: "UserDB" = Relationship(back_populates="card_market")
    user_card: "UserCardDB" = Relationship(back_populates="card_market")
    card: "CardDB" = Relationship(back_populates="card_market")


class ExchangeType(Enum):
    on_sale = "on_sale"
    on_exchange = "on_exchange"


GRADE_COST: int = 2500

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