from flask import Blueprint, jsonify
from src.cache import cache
import csv
import requests
import re

from datetime import datetime, timedelta

root = Blueprint('root', __name__)

DATASET = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-%s.csv" # noqa
DATASET_ALL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv" # noqa
DEFAULT_KEYS = ['Confirmed', 'Deaths', 'Recovered']
TODAY = datetime.utcnow().date()
YESTERDAY_STR = {
    "slash": datetime.strftime(TODAY - timedelta(1), "%-m/%d/%y"),
    "hyphen": datetime.strftime(TODAY - timedelta(1), "%m-%d-%Y")
}
TODAY_STR = {
    "slash": TODAY.strftime("%-m/%d/%y"),
    "hyphen": TODAY.strftime("%m-%d-%Y")
}


@root.route('/')
@root.route('/summary')
@cache.cached(timeout=300)
def index():
    data = {
        "Confirmed": 0,
        "Deaths": 0,
        "Recovered": 0,
    }

    for item in _get_today():
        data['Confirmed'] += int(item['Confirmed'])
        data['Deaths'] += int(item['Deaths'])
        data['Recovered'] += int(item['Recovered'])

    return jsonify(data), 200


@root.route('/all')
@cache.cached(timeout=300)
def all_data():
    return jsonify(_get_today()), 200


def _get_today():
    get_data = _extract_handler(DATASET_ALL % TODAY_STR['hyphen'])
    if not get_data:
        get_data = _extract_handler(DATASET_ALL % YESTERDAY_STR['hyphen'])

    return [{re.sub('[/ ]', '', key):
             int(item[key]) if key in DEFAULT_KEYS else
             None if item[key] == "" else item[key] for key in item}
            for item in get_data]


def _extract_handler(url):
    request = requests.get(url)

    if not request.status_code == 200:
        return False

    return [item for item in csv.DictReader(request.text.splitlines())]
