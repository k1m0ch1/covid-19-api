from flask import Blueprint, jsonify
from src.cache import cache
from datetime import datetime, timedelta
from dateutil import parser

import json
import csv
import requests
import re

from src.helper import (
    is_bot, is_not_bot,
    TODAY_STR, YESTERDAY_STR, TODAY,
    HOTLINE
)

from src.config import (
    sLIMITER, DATASET_ALL,
    NEWSAPI_HOST, NEWSAPI_KEY
)
from src.limit import limiter
from src import bot

root = Blueprint('root', __name__)

DEFAULT_KEYS = ['Confirmed', 'Deaths', 'Recovered']


@root.route('/')
@root.route('/status')
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

    if is_bot():
        return jsonify(message=bot.summary(data)), 200
    return jsonify(data), 200


@root.route('/hotline')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def hotline():
    if is_bot():
        return jsonify(message=bot.hotline(HOTLINE)), 200
    return jsonify(HOTLINE), 200


@root.route('/hotline/<state>')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def hot_line(state):
    results = []
    for city in HOTLINE:
        key = city["kota"].lower()
        if re.search(r"\b%s" % state.lower(), key):
            results.append(city)
    if is_bot():
        return jsonify(message=bot.hotline(results)), 200
    return jsonify(results)


@root.route('/<status>')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def stat(status):
    if is_bot():
        return jsonify(message="Not Found"), 404
    if status in ['confirmed', 'deaths', 'recovered']:
        return jsonify(_get_today(only_keys=status)), 200
    return jsonify(message="Not Found"), 404


@root.route('/provinces')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def provinces():
    if is_bot():
        return jsonify(message="Not Found"), 404
    with open('src/provinces.json', 'rb') as outfile:
        return jsonify(json.load(outfile)), 200
    return jsonify({"message": "Error Occured"}), 500


@root.route('/countries')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def countries():
    if is_bot():
        return jsonify(message="Not Found"), 404
    with open('src/countries.json', 'rb') as outfile:
        return jsonify(json.load(outfile)), 200
    return jsonify({"message": "Error Occured"}), 500


@root.route('/status/<country_id>')
@root.route('/countries/<country_id>')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def country(country_id):
    if is_bot():
        return jsonify(
            message=bot.countries(
                _get_today(country=country_id.upper(), mode="diff"))), 200
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

    if is_bot():
        return jsonify(message=bot.news(req.json()['articles'])), 200
    return jsonify(req.json()['articles']), 200


@root.route('/all')
@cache.cached(timeout=50)
def all_data():
    return jsonify(_get_today()), 200


def _get_today(**kwargs):
    now_data = TODAY_STR['hyphen']
    prev_data = YESTERDAY_STR['hyphen']
    get_data = _extract_handler(DATASET_ALL % TODAY_STR['hyphen'])

    if not get_data:
        now_data = YESTERDAY_STR['hyphen']
        prev_data = datetime.strftime(TODAY - timedelta(days=2), "%m-%d-%Y")
        get_data = _extract_handler(DATASET_ALL % now_data)

    result = [{f"{re.sub('[_]', '', key)[0].lower()}"
               f"{re.sub('[_]', '', key)[1:]}":
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

                curr_key = f"{re.sub('[_]', '', key)[0].lower()}" \
                    f"{re.sub('[_]', '', key)[1:]}"

                result[curr_index][curr_key] = \
                    int(item[key]) if key in DEFAULT_KEYS else \
                    None if item[key] == "" else item[key]
            curr_index += 1

    if "country" in kwargs:
        result = _country(kwargs['country'], get_data)

    if "mode" in kwargs:
        if kwargs['mode'] == "diff":
            result = {
                "origin": result,
                "diff": "",
                "last_updated": parser.parse(now_data).isoformat()
            }
            get_prev_data = _extract_handler(DATASET_ALL % prev_data)
            result['diff'] = _country(kwargs['country'], get_prev_data)

    return result


def _extract_handler(url):
    request = requests.get(url)

    if not request.status_code == 200:
        return False

    return [item for item in csv.DictReader(request.text.splitlines())]


def _country(negara, data):
    countries = None
    key_country = ""
    result = []
    with open('src/countries.json', 'rb') as outfile:
        countries = json.load(outfile)

    for country in countries["countries"]:
        if countries["countries"][country] == negara:
            key_country = country
            break
    for item in data:
        if item["Country_Region"] == key_country:
            result.append({})
            for key in item:
                curr_key = f"{re.sub('[_]', '', key)[0].lower()}" \
                    f"{re.sub('[_]', '', key)[1:]}"

                result[-1][curr_key] = \
                    int(item[key]) if key in DEFAULT_KEYS else \
                    None if item[key] == "" else item[key]

    return result
