from app.db.models import ExpansionDB
from sqlmodel import Session, select


def insert_expansion(session: Session, expansion):
    session.add(expansion)


def get_expansion_by_name(session: Session, name: str) -> ExpansionDB | None:
    card = session.exec(select(ExpansionDB).where(ExpansionDB.name == name)).first()
    return card


def get_expansion_by_id(session: Session, id: int) -> ExpansionDB | None:
    card = session.get(ExpansionDB, id)
    return card


def get_expansions(session: Session) -> list[ExpansionDB]:
    cards = session.exec(select(ExpansionDB)).all()
    return cards


def get_expansion_by_generation(session: Session, id_generation: int) -> list[ExpansionDB]:
    expansions = session.exec(select(ExpansionDB).where(ExpansionDB.id_generation==id_generation)).all()
    return expansions
