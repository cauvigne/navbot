"""
This file is part of Navbot.
Navbot is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Navbot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Foobar. If not, see
<https://www.gnu.org/licenses/>.
"""

import ast
import logging

import mariadb

from bot import DB_USER, DB_PWD, DB_HOST, DB_PORT, DB_DATABASE

logger = logging.getLogger(__name__)


def connect_db():
    # Connect to MariaDB Platform
    conn = mariadb.connect(
        user=DB_USER,
        password=DB_PWD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_DATABASE)
    cursor = conn.cursor(dictionary=True)
    return conn, cursor


def close_db(conn, cursor):
    cursor.close()
    conn.close()


def db_request(func):
    def inner_function(*args, **kwargs):
        conn = None
        cursor = None
        try:
            conn, cursor = connect_db()
        except mariadb.Error:
            logger.exception("Can't connect to mariadb database.")
        try:
            return func(conn, cursor, *args, **kwargs)
        except mariadb.Error as e:
            logger.exception("Can't execute mariadb request.", str(e))
        finally:
            close_db(conn, cursor)

    return inner_function


@db_request
def get_spam_ids(conn, cursor):
    cursor.execute("SELECT telegram_id FROM channel_user WHERE spam=1;")
    row = cursor.fetchall()
    return row


@db_request
def get_member_ids(conn, cursor):
    cursor.execute("SELECT telegram_id FROM channel_user;")
    return cursor.fetchall()


@db_request
def add_spam_id(conn, cursor, username: str, user_contact: str, telegram_id: str):
    logger.info("Add %s to spam ids" % telegram_id)
    cursor.execute(
        "INSERT INTO channel_user(name,telegram_id,user_contact,spam) VALUES (?,?,?,?) ON DUPLICATE KEY UPDATE name=VALUES(name), user_contact=VALUES(user_contact)",
        (username, telegram_id, user_contact, 1))
    conn.commit()


'''
Query today shuttles as shown below
Result example: "[{'datetime': datetime.datetime(2023, 8, 13, 23, 30), 'status': 'ok', 'seats': '8pl'}]"
'''


@db_request
def get_today_shuttle(conn, cursor):
    cursor.callproc("get_today_shuttles")
    row = cursor.fetchall()
    return row


'''
Get next days shuttle (not today shuttles)
Result example: [[{'datetime': datetime.datetime(2023, 8, 15, 23, 30), 'status': 'ok', 'seats': '8pl'}]]

'''


@db_request
def get_next_shuttles(conn, cursor):
    cursor.callproc("list_next_shuttles")
    row = cursor.fetchall()
    row_hour = []
    for i in row:
        cursor.callproc("get_day_shuttles", (i['date'],))
        row_hour.append(cursor.fetchall())
    return row_hour


''' Get a list of all shutlles timestamp
Result example: ['2023-08-13 23:30', '2023-08-15 23:30']
'''


@db_request
def get_next_shuttles_timestamp(conn, cursor):
    cursor.callproc("list_future_shuttles_timestamp")
    res = cursor.fetchall()
    if res:
        res = [i['datetime'].strftime('%Y-%m-%d %H:%M') for i in res]
    return res


@db_request
def query_add_shuttle(conn, cursor, time_st: str):
    cursor.callproc("add_shuttle", (time_st,))
    row = cursor.fetchone()
    return row


'''
Invoke the remove_shuttle called procedure for a given timestamp
'''


@db_request
def query_remove_shuttle(conn, cursor, time_st: str):
    cursor.callproc("remove_shuttle", (time_st,))
    row = cursor.fetchone()
    return row


'''
Book a shuttle
'''


@db_request
def query_book_shuttle(conn, cursor, timestamp: str, name: str, nb: int, user_id: str):
    cursor.callproc("book_shuttle", (timestamp, name, nb, user_id))
    cursor.execute("SELECT * FROM book_shuttle_table")
    row = cursor.fetchone()
    return row


@db_request
def query_get_enrolled(conn, cursor, timestamp: str):
    cursor.execute("Select * from shuttle WHERE `datetime`=\"%s\"" % timestamp)
    if not len(cursor.fetchall()):
        return None
    cursor.callproc("get_enrolled", (timestamp,))
    row = cursor.fetchall()
    return row


def query_nbseats(timestamp: str, user_id: str):
    res = query_get_enrolled(timestamp)
    if res is None:
        return 0
    for i in res:
        if i['user_id'] == str(user_id):
            return int(i['nbtot'])
    return 0


@db_request
def query_free_seats_nb(conn, cursor, timestamp: str):
    cursor.callproc("get_freeseats_number", (timestamp,))
    row = cursor.fetchone()
    if row['free_seats'] is None:
        return 8
    return int(row['free_seats'])


@db_request
def get_private_msg_ids(conn, cursor):
    cursor.execute("Select ids_values from msg_ids where `id`=1")
    res = cursor.fetchone()
    if res and "ids_values" in res.keys():
        return ast.literal_eval(res['ids_values'])
    return {}


@db_request
def set_private_msg_ids(conn, cursor, msg_ids: dict):
    cursor.execute(
        "Update  msg_ids set `ids_values` =\"%s\" where `id`=1" % str(msg_ids).replace("'", "\'").replace('"', '\"'))
    conn.commit()
