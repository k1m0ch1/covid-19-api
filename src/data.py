import csv
import requests
import re

from datetime import datetime, timedelta
from flask import jsonify

DATASET = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-%s.csv"
DATE_MATCHER = re.compile(r'\d{2}-\d{2}-\d{2}')
BASE_KEYS = ["Province/State", "Country/Region", "Lat", "Long"]
DEFAULT_KEYS = ["ProvinceState", "CountryRegion", "Lat", "Long"]
TODAY = datetime.utcnow().date()
YESTERDAY_STR = datetime.strftime(TODAY - timedelta(1), "%-m/%d/%y")
TODAY_STR = TODAY.strftime("%-m/%d/%y")


def case():
    data = []

    for status in ["confirmed", "deaths", "recovered"]:
        for indx, row in enumerate(_extract_handler(status)):
            if status == "confirmed":
                data_build = {
                        DEFAULT_KEYS[index]: row[key]
                        for index, key in enumerate(BASE_KEYS)
                }

                date_keys = [key for key in row if key not in BASE_KEYS]

                data_build[status] = int(row[TODAY_STR]) \
                    if TODAY_STR in date_keys else int(row[YESTERDAY_STR])

                data.append(data_build)
            else:
                data[indx][status] = int(row[TODAY_STR]) \
                    if TODAY_STR in date_keys else int(row[YESTERDAY_STR])

    return data


def _extract_handler(status):
    request = requests.get(DATASET % status.capitalize())

    if not request.status_code == 200:
        return False

    return [item for item in csv.DictReader(request.text.splitlines())]


def _country_dataset():
    return [item for item in
            csv.DictReader(open('src/country.csv', 'r'))]


def _get_country_code(country_name: str):
    country = _country_dataset()
    country_keys = [key['name'] for key in country]
    print(country_name)
    if country_name in country_keys:
        return country[country_keys.index(country_name)]['alpha-2']
    else:
        return country[_country_fix(country_name)]['alpha-2']


def _country_fix(country_name):
    data = {
        "Brunei": "Brunei Darussalam"
    }

    return data[country_name]
