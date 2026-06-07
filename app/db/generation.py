from app.db.models import GenerationDB
from sqlmodel import Session, select

def insert_generation(session: Session, generations):
    session.add(generations)


def get_generation_by_name(session: Session, name: str) -> GenerationDB | None:
    card = session.exec(select(GenerationDB).where(GenerationDB.name == name)).first()
    return card


def get_generation_by_id(session: Session, id: int) -> GenerationDB | None:
    card = session.get(GenerationDB, id)
    return card


def get_generations(session: Session) -> list[GenerationDB]:
    cards = session.exec(select(GenerationDB)).all()
    return cards