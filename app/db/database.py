import os
import mariadb
from pydantic import BaseModel

db_config = {
    'host': 'myapidb',
    'port': 3306,
    'user': 'dr_mundo',
    'password': 'mundo_no_recuerda_cuando_mundo_era_mundo',
    'database': 'mundo'
}

# =============== USER ===============
class UserDB(BaseModel):
    id: int | None = None
    username: str
    password: str
    name: str
    email:str
    money: float = 0
    address: str | None = None
    exchanges: int = 0


def insert_user(user: UserDB) -> id:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = "insert into user (name, username, password, email, money, address, exchanges) values (?, ?, ?, ?, ?, ?, ?)"
            values = (
                user.name, 
                user.username, 
                user.password,
                user.email,
                user.money,
                user.address,
                user.exchanges)
            cursor.execute(sql, values)
            conn.commit()
            return cursor.lastrowid


def get_user_by_username(username: str) -> UserDB | None:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql: str = "select * from user where username = ?"
            cursor.execute(sql, (username, ))
            row: list = cursor.fetchone()
            if row is None:
                return None
            return UserDB(
                id=row[0],
                name = row[1],
                username = row[2],
                password = row[3],
                email = row[4],
                money = row[5],
                address = row[6],
                exchanges = row[7]
            )


def get_users() -> list[UserDB]:
    lista: list[UserDB] = []
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql: str = "select * from user"
            cursor.execute(sql)
            rows: list = cursor.fetchall()
            for row in rows:
                lista.append(
                    UserDB(
                        id=row[0],
                        name = row[1],
                        username = row[2],
                        password = row[3],
                        email = row[4],
                        money = row[5],
                        address = row[6],
                        exchanges = row[7]
                    )
                )
    return lista

# =============== CARD ===============
class CardDB(BaseModel):
    id: int | None = None
    id_expansion: int
    name: str
    rarity: str
    frontcard: str | None = None
    backcard: str | None = None


def insert_card(card: CardDB) -> id:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = "insert into card (id_expansion, name, rarity, frontcard, backcard) values (?, ?, ?, ?, ?)"
            values = (
                card.id_expansion,
                card.name,
                card.rarity,
                card.frontcard,
                card.backcard)
            cursor.execute(sql, values)
            conn.commit()
            return cursor.lastrowid


def get_card_by_name(name: str) -> CardDB | None:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql: str = "select * from card where name = ?"
            cursor.execute(sql, (name, ))
            row: list = cursor.fetchone()
            if row is None:
                return None
            return CardDB(
                id=row[0],
                id_expansion=row[1],
                name=row[2],
                rarity=row[3],
                frontcard=row[4],
                backcard=row[5]
            )


def get_cards() -> list[CardDB]:
    lista: list[CardDB] = []
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql: str = "select * from card"
            cursor.execute(sql)
            rows: list = cursor.fetchall()
            for row in rows:
                lista.append(
                    CardDB(
                        id=row[0],
                        id_expansion=row[1],
                        name=row[2],
                        rarity=row[3],
                        frontcard=row[4],
                        backcard=row[5]
                    )
                )
    return lista
# TODO: terminar los que quedan
# =============== EXPANSION ===============
'''class Expansion(BaseModel):
    id: int | None = None
    id_generation'''


# =============== GENERATION ===============



# =============== USER_CARD ===============



# =============== TRANSACTION ===============



# =============== TRADE ===============



