from app.db.models import UserCardDB
from sqlmodel import Session, select, col
from .card import CardDB


def create_user_card(session: Session, user_card) -> None:
    session.add(user_card)


def get_user_cards(session: Session, id_user: int, offset: int, limit: int) -> list[UserCardDB]:
    user_cards = session.exec(select(UserCardDB).where(UserCardDB.id_user == id_user).offset(offset).limit(limit)).all()
    id_cards: set = set([card.id_card for card in user_cards])
    cards = session.exec(select(CardDB).where(col(CardDB.id).in_(list(id_cards)))).all()
    return [user_cards, cards]


def get_user_card_by_id(session: Session, id: int) -> UserCardDB:
    return session.get(UserCardDB, id)


def get_user_card_by_card_id(session: Session, id_user: int, id_card: int, psa: int | None) -> UserCardDB:
    return session.exec(select(UserCardDB).where(UserCardDB.id_user == id_user).where(UserCardDB.id_card == id_card).where(UserCardDB.psa == psa)).first()


def get_user_cards_by_expansion(session: Session, id_user: int, id_expansion: int, limit: int, offset: int):
    statement = select(UserCardDB).join(CardDB, UserCardDB.id_card == CardDB.id)
    statement = statement.where(UserCardDB.id_user == id_user).where(CardDB.id_expansion == id_expansion)
    statement = statement.offset(offset).limit(limit)
    user_cards = session.exec(statement).all()
    id_cards: set = set([card.id_card for card in user_cards])
    cards = session.exec(select(CardDB).where(col(CardDB.id).in_(list(id_cards)))).all()
    return [user_cards, cards]


def update_user_card(
    session: Session,
    id: int | None = None,
    id_user: int | None = None,
    id_card: int | None = None,
    price: int | None = None,
    psa: int | None = None,
    sold: bool | None = None
) -> UserCardDB:
    user_card = session.exec(select(UserCardDB).where(UserCardDB.id == id)).first()
    user_card.id_user = user_card.id_user if id_user is None else id_user
    user_card.id_card = user_card.id_card if id_card is None else id_card
    user_card.price = user_card.price if price is None else price
    user_card.psa = user_card.psa if psa is None else psa
    user_card.sold = user_card.sold if sold is None else sold
    
    session.add(user_card)
    session.flush()
    return user_card


def remove_card(session: Session, id: int) -> UserCardDB:
    card = session.exec(select(UserCardDB).where(UserCardDB.id == id)).one()
    session.delete(card)
    return card