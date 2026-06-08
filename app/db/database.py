from app.db.user import UserDB
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///app/db/data.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

def get_session():
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.flush()
        session.commit()


def create_database_and_tables():
    SQLModel.metadata.create_all(engine)


def create_admin_user(passwd: str):
    session: Session = next(get_session())
    admin = UserDB(
        name = "admin",
        username = "admin",
        password = passwd,
        email = "admin@laxodo.com",
        money = 9999999.00,
        is_admin = True
    )
    try:
        session.add(admin)
        session.commit()
        session.refresh(admin)
    except Exception:
        pass