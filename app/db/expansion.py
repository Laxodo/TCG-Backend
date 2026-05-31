from sqlmodel import SQLModel, Field, Session, select, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .card import CardDB
    from .generation import GenerationDB
    from .expansion import ExpansionDB

    

class ExpansionDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_generation: int = Field(index=True, foreign_key="generationdb.id")
    name: str = Field(index=True)
    price: int = Field(index=True)
    year: int = Field(index=True)

    generation: "GenerationDB" = Relationship(back_populates="expansions")
    cards: list["CardDB"] = Relationship(back_populates="expansion")


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
