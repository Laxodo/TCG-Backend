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
    id: int
    username: str
    password: str
    name: str
    email:str
    money: str
    address: str 
    exanges: int


def insert_user(user: UserDB) -> id:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = "insert into users (name, username, password) values (?, ?, ?)"
            values = (user.name, user.username, user.password)
            cursor.execute(sql, values)
            conn.commit()
            return cursor.lastrowid


def get_user_by_username(username: str) -> UserDB | None:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = "select username from users where username like ?"
            cursor.execute(sql, username)
            usernameDB: str | None = None
            for row in cursor:
                 usernameDB = row[0]
            conn.commit()
            return usernameDB

