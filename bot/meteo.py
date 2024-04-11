"""
This file is part of Navbot.
Navbot is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Navbot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Foobar. If not, see
<https://www.gnu.org/licenses/>.
"""

import re
from datetime import datetime

import requests

coordinates = {'Chesieres': [7.037019, 46.297936], 'Roc': [7.061603, 46.316877], 'Meilleret': [7.138238, 46.337745]}


def get_soaring_data(day: datetime = None):
    data = {}
    if day is None:
        day = datetime.now()
    res = requests.get(
        "https://soaringmeteo.org/soarWRF/%s/dataSoarWrf2Klatest.js" % day.strftime(
            "%Y-%m-%d"))
    if res.status_code != 200:
        return None

    for loc in coordinates.keys():
        resu = re.search(
            'los\[[0-9]+\]=' + str(coordinates[loc][0]) + ';las\[[0-9]+\]=' + str(
                coordinates[loc][1]) + '.*els\[\d+\]=(\d+).*BLDsb\[\d+\]=(\d+).*BLDsc\[\d+\]=(\d+).*\n',
            res.content.decode())

        data[loc] = {'plaf': [int(resu.group(1)) + int(resu.group(2)), int(resu.group(1)) + int(resu.group(3))]}
    return data


def get_meteo_message(day: datetime = None):
    try:
        data = get_soaring_data(day)
        msg = "Prévisions soaringmeteo.org:\n"
        for loc in data.keys():
            msg += loc + ": top couche convective: %d (12Z), %d (15Z)\n" % (data[loc]['plaf'][0], data[loc]['plaf'][1])
        return msg
    except Exception as e:
        return ""


if __name__ == "__main__":
    # get_soaring_data()
    print(get_meteo_message())
