from flask import Blueprint, jsonify
from src.cache import cache
from os import environ

import json
import csv
import requests
import re

from datetime import datetime, timedelta
from dateutil import parser
from src.db import session
from src.models import Status

root = Blueprint('root', __name__)

_ = environ.get
DATASET = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-%s.csv" # noqa
DATASET_ALL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv" # noqa
JABAR = 'https://coredata.jabarprov.go.id/analytics/covid19/aggregation.json'
DEFAULT_KEYS = ['Confirmed', 'Deaths', 'Recovered']
TODAY = datetime.utcnow().date()
NEWSAPI_KEY = _('NEWSAPI_KEY', "xxxxxxxxxx")
NEWSAPI_HOST = _('NEWSAPI_HOST', "http://newsapi.org/v2/top-headlines")
YESTERDAY_STR = {
    "slash": datetime.strftime(TODAY - timedelta(days=1), "%-m/%d/%y"),
    "hyphen": datetime.strftime(TODAY - timedelta(days=1), "%m-%d-%Y"),
    "hyphen-dmy": datetime.strftime(TODAY - timedelta(days=1), "%d-%m-%Y"),
}
TODAY_STR = {
    "slash": TODAY.strftime("%-m/%d/%y"),
    "hyphen": TODAY.strftime("%m-%d-%Y"),
    "hyphen-dmy": TODAY.strftime("%d-%m-%Y"),
}


@root.route('/')
@root.route('/summary')
@cache.cached(timeout=50)
def index():
    data = {
        "confirmed": 0,
        "deaths": 0,
        "recovered": 0,
    }

    for item in _get_today():
        data['confirmed'] += int(item['confirmed'])
        data['deaths'] += int(item['deaths'])
        data['recovered'] += int(item['recovered'])

    return jsonify(data), 200


@root.route('/confirmed')
def confirmed():
    return jsonify(_get_today(only_keys="confirmed")), 200


@root.route('/deaths')
def deaths():
    return jsonify(_get_today(only_keys="deaths")), 200


@root.route('/recovered')
def recovered():
    return jsonify(_get_today(only_keys="recovered")), 200


@root.route('/countries')
def countries():
    with open('src/countries.json', 'rb') as outfile:
        return jsonify(json.load(outfile)), 200
    return jsonify({"message": "Error Occured"}), 500


@root.route('/id')
def id():
    req = requests.get("https://kawalcovid19.harippe.id/api/summary")
    data = req.json()
    updated = parser.parse(data['metadata']['lastUpdatedAt']) \
        .replace(tzinfo=None)
    alldata = session.query(Status).order_by(Status.id.desc()).all()
    dbDate = ""
    if len(alldata) > 0:
        getData = [_id_beauty(data, row) for row in alldata]
        dbDate = parser.parse(getData[0]["metadata"]["last_updated"]) \
            .replace(tzinfo=None)
        if not updated == dbDate:
            new_status = Status(
                confirmed=data['confirmed']['value'],
                deaths=data['deaths']['value'],
                recovered=data['recovered']['value'],
                active_care=data['activeCare']['value'],
                country_id="id",
                created=updated,
                updated=updated
            )
            session.add(new_status)
        for row in getData:
            if not row['confirmed']['diff'] == 0 and \
               not row['deaths']['diff'] == 0 and \
               not row['recovered']['diff'] == 0 and \
               not row['active_care']['diff'] == 0:
                return jsonify(row), 200
        return jsonify(getData[0]), 200
    else:
        new_status = Status(
            confirmed=data['confirmed']['value'],
            deaths=data['deaths']['value'],
            recovered=data['recovered']['value'],
            active_care=data['activeCare']['value'],
            country_id="id",
            created=updated,
            updated=updated
        )
        session.add(new_status)
        return jsonify(_id_beauty(data, 0)), 200


@root.route('/countries/<country_id>')
def country(country_id):
    return jsonify(_get_today(country=country_id.upper())), 200


@root.route('/news/<countries>')
@root.route('/news')
@cache.cached(timeout=50)
def news(**kwargs):
    if NEWSAPI_KEY == "xxxxxxxxxx":
        return jsonify({"message": "Please provide the NewsApi API KEY"}), 500

    param = {"apiKey": NEWSAPI_KEY, "q": "corona",
             "pageSize": 3, "sources": "bbc-news"}

    if "countries" in kwargs:
        param["country"] = kwargs['countries']
        param.pop("sources")

    req = requests.get(NEWSAPI_HOST, params=param)

    if not req.status_code == 200:
        return jsonify({"message": "Error occured while "
                        "trying to get the news"}), req.status_code

    return jsonify(req.json()['articles']), 200


@root.route('/all')
@cache.cached(timeout=50)
def all_data():
    return jsonify(_get_today()), 200


def _get_today(**kwargs):
    get_data = _extract_handler(DATASET_ALL % TODAY_STR['hyphen'])
    if not get_data:
        get_data = _extract_handler(DATASET_ALL % YESTERDAY_STR['hyphen'])

    result = [{f"{re.sub('[/ ]', '', key)[0].lower()}"
               f"{re.sub('[/ ]', '', key)[1:]}":
               int(item[key]) if key in DEFAULT_KEYS else
               None if item[key] == "" else item[key] for key in item}
              for item in get_data]

    if "only_keys" in kwargs:
        basic_keys = ["confirmed", "deaths", "recovered"]
        basic_keys.pop(basic_keys.index(kwargs['only_keys']))
        result = []
        curr_index = 0
        for item in get_data:
            for key in item:
                if key.lower() in basic_keys:
                    continue
                result.append({})

                curr_key = f"{re.sub('[/ ]', '', key)[0].lower()}" \
                    f"{re.sub('[/ ]', '', key)[1:]}"

                result[curr_index][curr_key] = \
                    int(item[key]) if key in DEFAULT_KEYS else \
                    None if item[key] == "" else item[key]
            curr_index += 1

    if "country" in kwargs:
        countries = None
        key_country = ""
        result = []
        with open('src/countries.json', 'rb') as outfile:
            countries = json.load(outfile)

        for country in countries["countries"]:
            if countries["countries"][country] == kwargs['country']:
                key_country = country
                break
        for item in get_data:
            if item["Country/Region"] == key_country:
                result.append({})
                for key in item:
                    curr_key = f"{re.sub('[/ ]', '', key)[0].lower()}" \
                        f"{re.sub('[/ ]', '', key)[1:]}"

                    result[-1][curr_key] = \
                        int(item[key]) if key in DEFAULT_KEYS else \
                        None if item[key] == "" else item[key]

    return result


@root.route('/id/<state>')
def status_by_state(state):
    result = {}
    key_state = [
        'proses_pemantauan', 'proses_pengawasan', 'selesai_pemantauan',
        'selesai_pengawasan', 'total_odp', 'total_pdp', 'total_meninggal',
        'positif', 'sembuh', 'tanggal', 'total_positif_saat_ini',
        'total_sembuh'
    ]
    if 'jabar' in state:
        response = requests.get(JABAR)
        if not response.status_code == 200:
            jsonify({"message": f"Error when trying to crawl {JABAR}"}), 404
        json_resp = response.json()
        today_stat = _search_list(json_resp,
                                  "tanggal", TODAY_STR['hyphen-dmy'])
        yeday_stat = _search_list(json_resp,
                                  "tanggal", YESTERDAY_STR['hyphen-dmy'])
        for key in key_state:
            if today_stat[key] is None:
                result[key] = int(yeday_stat[key])
            else:
                result[key] = today_stat[key]

        result['source'] = "https://pikobar.jabarprov.go.id/"
        return jsonify(result), 200
    if len(result) == 0:
        jsonify({"message": "Not Found"}), 404
    return jsonify(result)


def _search_list(list, key, status_date):
    """ For List Search base on tanggal """

    for l in list:
        if l[key] == status_date:
            return l


def _extract_handler(url):
    request = requests.get(url)

    if not request.status_code == 200:
        return False

    return [item for item in csv.DictReader(request.text.splitlines())]


def _id_beauty(source, db):

    if db == 0:
        confirmed = 0
        deaths = 0
        recovered = 0
        active_care = 0
        updated = parser.parse(source['metadata']['lastUpdatedAt']) \
            .replace(tzinfo=None)
    else:
        confirmed = db.confirmed
        deaths = db.deaths
        recovered = db.recovered
        active_care = db.active_care
        updated = db.updated
    return {
        "confirmed": {
            "value": source['confirmed']['value'],
            "diff": source['confirmed']['value'] - confirmed
        },
        "deaths": {
            "value": source['deaths']['value'],
            "diff": source['deaths']['value'] - deaths
        },
        "recovered": {
            "value": source['recovered']['value'],
            "diff": source['recovered']['value'] - recovered
        },
        "active_care": {
            "value": source['activeCare']['value'],
            "diff": source['activeCare']['value'] - active_care
        },
        "metadata": {
            "country_id": "id",
            "last_updated": updated.isoformat()
        }
    }


def _is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parser.parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
