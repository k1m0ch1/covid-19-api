import requests
from datetime import datetime

from src.helper import DAERAH
from src.db import session
from src.models import Status

ODI_API = 'https://indonesia-covid-19.mathdro.id/api/provinsi'


def odi_api(state):
    req = requests.get(ODI_API)
    if not req.status_code == 200:
        return []
    prov = {prov["provinsi"]: prov for prov in req.json()["data"]}
    hasil = prov[DAERAH[state]]
    todayIsNone = True

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

    result['metadata'] = {
        "source": "https://indonesia-covid-19.mathdro.id/",
        "province": DAERAH[state].upper()
    }

    get_state = session.query(Status) \
        .filter(Status.country_id == f"id.{state}") \
        .order_by(Status.created.desc()) \
        .all()

    if len(get_state) > 0:
        for row in get_state:
            if not row.created.date() == datetime.utcnow().date():
                result["total_sembuh"]["diff"] = \
                    hasil["kasusSemb"] - row.recovered
                result["total_positif"]["diff"] = \
                    hasil["kasusPosi"] - row.confirmed
                result["total_meninggal"]["diff"] = \
                    hasil["kasusMeni"] - row.deaths
                result["metadata"]["diff_date"] = \
                    row.created.isoformat()
                result["metadata"]["source_date"] = \
                    datetime.utcnow().isoformat()
                break
            else:
                todayIsNone = False
                result["metadata"]["source_date"] = \
                    row.created.isoformat()

    if todayIsNone:
        new_status = Status(
            confirmed=hasil["kasusPosi"],
            deaths=hasil["kasusMeni"],
            recovered=hasil["kasusSemb"],
            active_care=0,
            country_id=f"id.{state}",
            created=datetime.utcnow(),
            updated=datetime.utcnow()
        )
        session.add(new_status)
        result["metadata"]["source_date"] = \
            datetime.utcnow().isoformat()

    result["total_sembuh"]["value"] = hasil["kasusSemb"]
    result["total_positif"]["value"] = hasil["kasusPosi"]
    result["total_meninggal"]["value"] = hasil["kasusMeni"]

    return result
