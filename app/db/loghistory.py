from app.db.models import LogActivityDB, LogHistoryDB
from app.tools.mappers import history_to_dto
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload, selectinload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from enum import Enum

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


def get_log_history_by_user_id(session: Session, user_id: int):
    statement = select(LogHistoryDB).where(LogHistoryDB.id_user == user_id).options(
        joinedload(LogHistoryDB.user),
        joinedload(LogHistoryDB.user_interacted),
        selectinload(LogHistoryDB.log_activity).options(
            joinedload(LogActivityDB.user),
            joinedload(LogActivityDB.card)
        )
    ).order_by(LogHistoryDB.id.desc())
    return paginate(session, statement, transformer=lambda items: [history_to_dto(item) for item in items])


def get_log_history_by_id(session: Session, id: int) -> LogHistoryDB:
    return session.get(LogHistoryDB, id)