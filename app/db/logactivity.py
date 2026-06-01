from sqlmodel import SQLModel, Field, Session, select, Relationship
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserDB
    from .card import CardDB
    from .loghistory import LogHistoryDB
    from .logactivity import LogActivityDB
    

class LogActivityDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_user: int = Field(index=True, foreign_key="userdb.id")
    id_card: int = Field(index=True, foreign_key="carddb.id")
    id_log_history: int = Field(index=True, foreign_key="loghistorydb.id")
    action: str = Field(index=True)
    price: int = Field(index=True)
    psa: int | None = Field(index=True)

    user: "UserDB" = Relationship(back_populates="log_activity")
    card: "CardDB" = Relationship(back_populates="log_activity")
    log_history: "LogHistoryDB" = Relationship(back_populates="log_activity")


class Action(Enum):
    GET = "get"
    LOST = "lost"


def create_log_activity(session: Session, log_activity: LogActivityDB) -> LogActivityDB:
    session.add(log_activity)
    session.flush()
    return log_activity


def get_log_activity(session: Session) -> list[LogActivityDB]:
    return session.exec(select(LogActivityDB)).all()


def get_log_activity_by_id(session: Session, id: int) -> LogActivityDB:
    return session.get(LogActivityDB, id)
