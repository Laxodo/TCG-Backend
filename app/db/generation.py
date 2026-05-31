from sqlmodel import SQLModel, Field, Session, select, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .expansion import ExpansionDB

    

class GenerationDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    year: int = Field(index=True)

    expansions: list["ExpansionDB"] = Relationship(back_populates="generation")


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

