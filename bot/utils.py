"""
This file is part of Navbot.
Navbot is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Navbot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Foobar. If not, see
<https://www.gnu.org/licenses/>.
"""

from datetime import datetime

from babel.dates import format_date
from telegram import User

from bot import CHANNEL_POST_URL
from bot.db import query_get_enrolled


def parse_datetime(args: list):
    try:
        if len(args) == 1:
            res = datetime.strptime(
                datetime.now().strftime("%Y-%m-%d ") + args[0], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
        elif len(args) == 2:
            res = datetime.strptime(' '.join(args), "%d-%m %H:%M").replace(year=datetime.now().year).strftime(
                "%Y-%m-%d %H:%M")
        else:
            res = None
        return res
    except Exception as e:
        # todo make a smarter error handling here
        return None


def parse_datetime_multiple(args: list):
    try:
        if len(args) == 1:
            res = [datetime.strptime(
                datetime.now().strftime("%Y-%m-%d ") + args[0], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")]
        elif len(args) > 1:
            res = []
            res_date = datetime.strptime(args[0], "%d-%m").replace(year=datetime.now().year).strftime(
                "%Y-%m-%d")
            for i in args[1:]:
                res.append(datetime.strptime(res_date + " " + i, "%Y-%m-%d %H:%M").strftime(
                    "%Y-%m-%d %H:%M"))
        else:
            res = None
        return res
    except Exception as e:
        # todo make a smarter error handling here
        return None


def parse_datetime_str(msg: str):
    if msg is None:
        return None
    try:
        return convert_userstr_to_datetime(msg).replace(year=datetime.now().year).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.strptime(msg, '%H:%M').replace(year=datetime.now().year, month=datetime.now().month,
                                                           day=datetime.now().day).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            # todo make a smarter error handling here
            return None


def format_notification_msg_channel(tstamp: list):
    tstamp_dt = [convert_isostr_to_datetime(i) for i in tstamp]
    thours_list = []
    for i in tstamp_dt:
        if 9 < i.hour < 19 and i.day == tstamp_dt[0].day and i.month == tstamp_dt[0].month:
            thours_list.append(i.strftime('%H:%M'))
    post_msg = "Navette ajoutée: %s à %s \n Réservation sur @asagirinav\_bot" % (
        format_date(tstamp_dt[0], format="full", locale="fr_CH"), ', '.join(thours_list))
    return post_msg


def format_notification_private(tstamp: str, nb_booked_seats: int):
    tstamp_dt = convert_isostr_to_datetime(tstamp)
    post_msg = "%s à *%s*\n  Mes réservations:  *%d* place(s).\n" % (
        format_date(tstamp_dt, format="full", locale="fr_CH"), tstamp_dt.strftime('%H:%M'), nb_booked_seats)
    post_msg += f"Statut temps réel: [canal Bus Asagiri]({CHANNEL_POST_URL}) "
    return post_msg


def get_shuttle_status(time_st: str) -> dict:
    if time_st is None:
        return {"status": "nok", "msg": "Désolé. Le format date-heure est incorrect."}
    res = query_get_enrolled(time_st)
    if res is None:
        return {"status": "nok", "msg": "Cette navette n'existe pas."}
    else:
        msg = f"Réservations actuelles pour la navette du {convert_datatime_to_user_date(time_st)}"
        for elem in res:
            msg += elem['user']
            if elem['user_contact']:
                msg += "( @%s)" % elem['user_contact']
            msg += ": " + str(elem['nbtot']) + " places\n"
        if not len(res):
            msg += "Pas de réservation."
        return {"status": "ok", "msg": msg}


def convert_isostr_to_datetime(tstamp: str):
    return datetime.strptime(tstamp, '%Y-%m-%d %H:%M')


def convert_userstr_to_datetime(tstamp: str):
    return datetime.strptime(tstamp, '%d-%m %H:%M')


def convert_datatime_to_user_date(tstamp: str):
    return datetime.strptime(tstamp, "%Y-%m-%d %H:%M").strftime("%d %B %Y à %H:%M:\n")


def convert_datetime_to_isostr(tstamp: datetime):
    return datetime.strftime(tstamp, '%Y-%m-%d %H:%M')


def build_user(user: User):
    user_str = user.first_name
    if user.last_name:
        user_str += " " + user.last_name
    if user.username:
        user_str += " @" + user.username
    return user_str
