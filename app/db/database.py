from sqlmodel import SQLModel, create_engine, Field, Session, select
import os

DATABASE_URL = "sqlite:///app/db/data.db"

class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str = Field(index=True)  
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    money: float | None = Field(default=0.0, index=True)
    address: str | None = Field(default=None, index=True)
    exchanges: int | None = Field(default=0, index=True)


class CardDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_expansion: int = Field(index=True)
    name: str = Field(index=True)
    rarity: str = Field(index=True)
    frontcard: str = Field(index=True)
    backcard: str = Field(index=True)
    

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


def create_database_and_tables():
    SQLModel.metadata.create_all(engine)


def insert_user(user):
    with Session(engine) as session:
        session.add(user)
        try:
            session.commit()
        except Exception:
            raise ValueError
        session.refresh(user)


def get_users() -> list[UserDB]:
    with Session(engine) as session:
        users = session.exec(select(UserDB)).all()
        return users


def get_user_by_username(username: str) -> UserDB:
    with Session(engine) as session:
        users = session.exec(select(UserDB).where(UserDB.username == username)).first()
        return users


def insert_card(card):
    with Session(engine) as session:
        session.add(card)
        try:
            session.commit()
        except Exception:
            raise ValueError
        session.refresh(card)


def get_cards() -> list[CardDB]:
    with Session(engine) as session:
        cards = session.exec(select(CardDB)).all()
        return cards


def get_card_by_name(name: str) -> CardDB:
    with Session(engine) as session:
        card = session.exec(select(CardDB).where(CardDB.name == name)).first()
        return card

# =============== EXPANSION ===============
class ExpansionDB(BaseModel):
    id: int | None = None
    id_generation: int
    name: str
    year: int


def insert_expansion(expansions: ExpansionDB) -> id:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = "insert into expansion (id_generation, name, year) values (?, ?, ?)"
            values = (
                expansions.id_generation,
                expansions.name,
                expansions.year
            )
            cursor.execute(sql, values)
            conn.commit()
            return cursor.lastrowid


def get_expansion_by_name(name: str) -> ExpansionDB | None:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql: str = "select * from expansion where name = ?"
            cursor.execute(sql, (name, ))
            row: list = cursor.fetchone()
            if row is None:
                return None
            return ExpansionDB(
                id=row[0],
                id_generation=row[1],
                name=row[2],
                year=row[3]
            )


def get_expansions() -> list[ExpansionDB]:
    lista: list[ExpansionDB] = []
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql: str = "select * from expansion"
            cursor.execute(sql)
            rows: list = cursor.fetchall()
            for row in rows:
                lista.append(
                    ExpansionDB(
                        id=row[0],
                        id_generation=row[1],
                        name=row[2],
                        year=row[3]
                    )
                )
    return lista


# =============== GENERATION ===============
class GenerationDB(BaseModel):
    id: int | None = None
    name: str
    year: int


def insert_generation(generations: GenerationDB) -> id:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = "insert into generation (name, year) values (?, ?)"
            values = (
                generations.name,
                generations.year
            )
            cursor.execute(sql, values)
            conn.commit()
            return cursor.lastrowid


def get_generation_by_name(name: str) -> GenerationDB | None:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = str = "select * from generation where name = ?"
            cursor.execute(sql, (name, ))
            row: list = cursor.fetchone()
            if row is None:
                return None
            return GenerationDB(
                id=row[0],
                name=row[1],
                year=row[2]
            )


def get_generations() -> list[GenerationDB]:
    lista: list[GenerationDB] = []
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql: str = "select * from generation"
            cursor.execute(sql)
            rows: list = cursor.fetchall()
            for row in rows:
                lista.append(
                    GenerationDB(
                        id=row[0],
                        name=row[1],
                        year=row[2]
                    )
                )
    return lista


# TODO: terminar los que quedan
# =============== USER_CARD ===============



# =============== TRANSACTION ===============



# =============== TRADE ===============

