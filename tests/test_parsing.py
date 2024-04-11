import datetime
import unittest

import pytest

from bot.booking.booking_cli import parse_reservation
from bot.utils import parse_datetime_multiple, format_notification_msg_channel


@pytest.mark.parametrize("test_input,expected", [(["13-05", "12:30"], ["2024-05-13 12:30"]), (
["13-05", "12:30", "13:30", "15:45"], ["2024-05-13 12:30", "2024-05-13 13:30", "2024-05-13 15:45"]), (
                                                 ["13:15"], [datetime.datetime.now().strftime("%Y-%m-%d") + " 13:15"])])
def test_parsing(test_input, expected):
    res = parse_datetime_multiple(test_input)
    assert (res == expected)


@pytest.mark.parametrize("test_input,expected", [(["2024-05-13 12:30"], "Navette ajoutée: lundi, 13 mai 2024 à 12:30"),
                                                 (["2024-05-13 12:30", "2024-05-13 13:30", "2024-05-13 23:00",
                                                   "2024-05-14 12:00"],
                                                  "Navette ajoutée: lundi, 13 mai 2024 à 12:30, 13:30 ")])
def test_notif_msg_channel(test_input, expected):
    res = format_notification_msg_channel(test_input)
    assert (res.startswith(expected))


@pytest.mark.parametrize("test_input,expected", [("+1 12:30", {"fct": '+', "nb": 1, "timest": "12:30"})])
def test_user_parsing(test_input, expected):
    res = parse_reservation(test_input)
    assert (res == expected)


if __name__ == '__main__':
    unittest.main()
