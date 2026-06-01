from sqlmodel import SQLModel, Field, Session, select, Relationship
from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserDB
    from .loghistory import LogHistoryDB
    from .logactivity import LogActivityDB

    

class LogHistoryDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_user: int = Field(index=True, foreign_key="userdb.id")
    id_user_interacted: int | None = Field(index=True, foreign_key="userdb.id")
    description: str = Field(index=True)
    type: str = Field(index=True)
    money_exchange: int = Field(default=0, index=True)
    date: str | None = Field(default=datetime.now() ,index=True)

    log_activity: list["LogActivityDB"] = Relationship(back_populates="log_history")
    user: "UserDB" = Relationship(back_populates="log_history", sa_relationship_kwargs={"foreign_keys": "LogHistoryDB.id_user"})
    user_interacted: "UserDB" = Relationship(back_populates="log_history_interacted", sa_relationship_kwargs={"foreign_keys": "LogHistoryDB.id_user_interacted"})


class LogType(Enum):
    SALE = "sale"
    EXCHANGE = "exchange"
    OPEN_BOOSTER = "open_booster"
    QUICK_SELL = "quick_sell"
    GRADE = "grade"


def create_log_history(session: Session, log_history: LogHistoryDB) -> LogHistoryDB:
    session.add(log_history)
    session.flush()
    return log_history


def get_log_history(session: Session) -> list[LogHistoryDB]:
    return session.exec(select(LogHistoryDB)).all()


def get_log_history_by_id(session: Session, id: int) -> LogHistoryDB:
    return session.get(LogHistoryDB, id)
