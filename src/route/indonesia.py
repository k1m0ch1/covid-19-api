import requests
import re
from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from dateutil import parser

from src.cache import cache
from src.db import session
from src.limit import limiter
from src.models import Status
from src.helper import (
    is_empty, is_bot, is_not_bot,
    TODAY_STR, TODAY, YESTERDAY_STR,
    HOTLINE
)

indonesia = Blueprint('indonesia', __name__)
JABAR = 'https://coredata.jabarprov.go.id/analytics/covid19/aggregation.json'
ODI_API = 'https://indonesia-covid-19.mathdro.id/api/provinsi'
KAWAL_COVID = "https://kawalcovid19.harippe.id/api/summary"
CONTACT = "https://pikobar.jabarprov.go.id/contact/"
sLIMITER = 5


@indonesia.route('/')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def id():
    req = requests.get(KAWAL_COVID)
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


@indonesia.route('/hotline')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def hotline():
    return jsonify(HOTLINE), 200


@indonesia.route('/hotline/<state>')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def hot_line(state):
    results = []
    for city in HOTLINE:
        key = city["kota"].lower()
        if re.search(r"\b%s" % state.lower(), key):
            results.append(city)
    return jsonify(results)


@indonesia.route('/jabar')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def jabar():
    result = _default_resp()
    result['source'] = {"value": "https://pikobar.jabarprov.go.id/"}

    response = requests.get(JABAR)
    if not response.status_code == 200:
        jsonify({"message": f"Error when trying to crawl {JABAR}"}), 404
    json_resp = response.json()
    today_stat = _search_list(json_resp,
                              "tanggal", TODAY_STR['hyphen-dmy'])
    yeday_stat = _search_list(json_resp,
                              "tanggal", YESTERDAY_STR['hyphen-dmy'])

    if today_stat["selesai_pengawasan"] is None:
        twodaysago = _search_list(
            json_resp, "tanggal",
            datetime.strftime(TODAY - timedelta(days=2), "%d-%m-%Y"))
        result = _jabarset_value(yeday_stat, twodaysago)
    else:
        result = _jabarset_value(today_stat, yeday_stat)

    if len(result) == 0:
        jsonify({"message": "Not Found"}), 404

    return jsonify(result), 200


@indonesia.route('/jakarta')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def jakarta():
    return _odi_api("jakarta")


@indonesia.route('/banten')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def banten():
    return _odi_api("banten")


@indonesia.route('/bali')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def bali():
    return _odi_api("bali")


@indonesia.route('/yogya')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def yogya():
    return _odi_api("yogya")


@indonesia.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"message": "Rate Limited"}), 429


def _default_resp():
    return {
        "tanggal": {"value": ""},
        "total_sembuh": {"value": 0, "diff": 0},
        "total_positif_saat_ini": {"value": 0, "diff": 0},
        "total_meninggal": {"value": 0, "diff": 0},
        "proses_pemantauan": {"value": 0},
        "proses_pengawasan": {"value": 0},
        "selesai_pemantauan": {"value": 0},
        "selesai_pengawasan": {"value": 0},
        "total_odp": {"value": 0},
        "total_pdp": {"value": 0},
        "source": {"value": ""}
    }


def _search_list(list, key, status_date):
    """ For List Search base on tanggal """

    for l in list:
        if l[key] == status_date:
            return l


def _jabarset_value(current, before):
    result = {}
    keys = [
        'meninggal', 'positif', 'proses_pemantauan', 'proses_pengawasan',
        'selesai_pemantauan', 'selesai_pengawasan', 'sembuh',
        'tanggal', 'total_meninggal', 'total_odp', 'total_pdp',
        'total_positif_saat_ini', 'total_sembuh'
    ]
    for key in keys:
        if key not in \
            ["tanggal", "meninggal", "positif",
                "selesai_pengawasan", "proses_pemantauan"]:
            result[key] = {
                "value": int(is_empty(current[key])),
                "diff": int(is_empty(current[key])) -
                int(is_empty(before[key]))
            }
        else:
            result[key] = {"value": int(is_empty(current[key]))
                           if not key == "tanggal" else
                           is_empty(current[key])}
    return result


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


def _odi_api(state):
    result = _default_resp()
    result['source'] = {"value": "https://indonesia-covid-19.mathdro.id/"}

    req = requests.get(ODI_API)
    if not req.status_code == 200:
        jsonify({"message": f"Error when trying to crawl {ODI_API}"}), 404
    prov = {prov["provinsi"]: prov for prov in req.json()["data"]}

    daerah = {
        "jakarta": "DKI Jakarta",
        "banten": "Banten",
        "bali": "Bali",
        "yogya": "Daerah Istimewa Yogyakarta"
    }

    hasil = prov[daerah[state]]

    result["total_sembuh"]["value"] = hasil["kasusSemb"]
    result["total_positif_saat_ini"]["value"] = hasil["kasusPosi"]
    result["total_meninggal"]["value"] = hasil["kasusMeni"]

    if len(result) == 0:
        jsonify({"message": "Not Found"}), 404

    return jsonify(result), 200
