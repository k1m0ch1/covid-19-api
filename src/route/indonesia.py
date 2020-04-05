import requests
from wand.image import Image
from flask import Blueprint, jsonify, Response, url_for
from datetime import datetime, timedelta
from dateutil import parser
from base64 import b64decode

from src.cache import cache
from src.db import session
from src.limit import limiter
from src.models import Status, Attachment
from src import seeder
from src.helper import (
    is_empty, is_bot, is_not_bot,
    TODAY_STR, TODAY, YESTERDAY_STR,
    DAERAH
)
from src import bot, config, crawler

indonesia = Blueprint('indonesia', __name__)
JABAR = 'https://coredata.jabarprov.go.id/analytics/covid19/aggregation.json'

KAWAL_COVID = "https://kawalcovid19.harippe.id/api/summary"
CONTACT = "https://pikobar.jabarprov.go.id/contact/"
DATASET_CONFIRMED = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv" # noqa
DATASET_RECOVERED = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv" # noqa
DATASET_DEATHS = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv" # noqa
sLIMITER = config.sLIMITER


@indonesia.route('/graph')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def graph():
    get_latest = session.query(Attachment) \
        .filter(Attachment.key == "graph.harian") \
        .order_by(Attachment.created.desc()) \
        .first()
    scr_png = b64decode(get_latest.attachment)
    scr_img = Image(blob=scr_png)
    return Response(scr_img.make_blob(), mimetype='image/jpeg')


@indonesia.route('/seed')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def seed():
    seeder.seed()


@indonesia.route('/')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def id():
    req = requests.get(KAWAL_COVID)
    data = req.json()
    updated = parser.parse(data['metadata']['lastUpdatedAt']) \
        .replace(tzinfo=None)
    alldata = session.query(Status) \
        .filter(Status.country_id == "id") \
        .order_by(Status.created.desc()).all()
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
        for index, row in enumerate(getData):
            if not row['confirmed']['diff'] == 0 and \
               not row['deaths']['diff'] == 0 and \
               not row['recovered']['diff'] == 0 and \
               not row['active_care']['diff'] == 0:
                row['metadata']['last_updated'] = \
                    getData[index-1]['metadata']['last_updated']
                return _response(row, 200)
        return _response(getData[0], 200)
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
        return _response(_id_beauty(data, 0), 200)


@indonesia.route('/jabar')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def jabar():
    result = {
        "tanggal": {"value": ""},
        "total_sembuh": {"value": 0, "diff": 0},
        "total_positif": {"value": 0, "diff": 0},
        "total_meninggal": {"value": 0, "diff": 0},
        "proses_pemantauan": {"value": 0},
        "proses_pengawasan": {"value": 0},
        "selesai_pemantauan": {"value": 0},
        "selesai_pengawasan": {"value": 0},
        "total_odp": {"value": 0},
        "total_pdp": {"value": 0},
        "source": {"value": ""}
    }

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

    result['source'] = {"value": "https://pikobar.jabarprov.go.id/"}
    return jsonify(result), 200


@indonesia.route('/<province>')
@limiter.limit(f"1/{sLIMITER}second", key_func=lambda: is_bot(), exempt_when=lambda: is_not_bot()) # noqa
@cache.cached(timeout=50)
def province(province):
    if province in DAERAH:
        result = crawler.odi_api(province)
        if len(result) == 0:
            return jsonify(message="Not Found"), 404

        if is_bot():
            return jsonify(message=bot.province(result)), 200
        else:
            return jsonify(result), 200

    if province == "list":
        provinsi = [item for item in DAERAH]
        if True:
            return jsonify(message=bot.province_list(provinsi)), 200
        else:
            return jsonify([item for item in DAERAH]), 200
    return jsonify(message="Not Found"), 404


@indonesia.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"message": "Rate Limited"}), 429


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
        updated = db.created
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


def _response(data, responseCode):
    if is_bot():
        return jsonify(
            message=bot.id(data),
            images=[url_for('indonesia.graph', _external=True)]), responseCode
    else:
        return jsonify(data), responseCode

