from app.db.models import LogActivityDB
from sqlmodel import Session, select
from enum import Enum

class Action(Enum):
    GET = "get"
    LOST = "lost"


def create_log_activity(session: Session, log_activity: LogActivityDB) -> LogActivityDB:
    session.add(log_activity)
    session.flush()
    return log_activity


def get_log_activity(session: Session) -> list[LogActivityDB]:
    statement = select(LogActivityDB).options(
        joinedload(LogActivityDB.user),
        joinedload(LogActivityDB.user_card),
        joinedload(LogActivityDB.log_history)
    )
    return session.exec(statement).all()


def get_log_activity_by_id(session: Session, id: int) -> LogActivityDB:
    return session.get(LogActivityDB, id)
