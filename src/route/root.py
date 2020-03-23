from flask import Blueprint, jsonify
from src.cache import cache
from os import environ

import json
import csv
import requests
import re

from src.helper import (
    is_bot, is_not_bot,
    TODAY_STR, YESTERDAY_STR
)
from src.limit import limiter

root = Blueprint('root', __name__)

_ = environ.get
DATASET_ALL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv" # noqa
DEFAULT_KEYS = ['Confirmed', 'Deaths', 'Recovered']
NEWSAPI_KEY = _('NEWSAPI_KEY', "xxxxxxxxxx")
NEWSAPI_HOST = _('NEWSAPI_HOST', "http://newsapi.org/v2/top-headlines")
sLIMITER = 5


@root.route('/')
@root.route('/summary')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
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
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def confirmed():
    return jsonify(_get_today(only_keys="confirmed")), 200


@root.route('/deaths')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def deaths():
    return jsonify(_get_today(only_keys="deaths")), 200


@root.route('/recovered')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def recovered():
    return jsonify(_get_today(only_keys="recovered")), 200


@root.route('/countries')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def countries():
    with open('src/countries.json', 'rb') as outfile:
        return jsonify(json.load(outfile)), 200
    return jsonify({"message": "Error Occured"}), 500


@root.route('/countries/<country_id>')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def country(country_id):
    return jsonify(_get_today(country=country_id.upper())), 200


@root.route('/news/<countries>')
@root.route('/news')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
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


def _extract_handler(url):
    request = requests.get(url)

    if not request.status_code == 200:
        return False

    return [item for item in csv.DictReader(request.text.splitlines())]
