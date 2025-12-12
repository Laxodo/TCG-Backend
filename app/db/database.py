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