#!/usr/bin/python3


import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def mysql_insert_update(change_sql, host, user, password, database):
    db = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(change_sql)
    db.commit()
    db.close()


def mysql_select(select_sql, host, user, password, database):
    db = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(select_sql)
    result = cursor.fetchall()
    db.close()
    return result
