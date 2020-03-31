from datetime import datetime, timedelta
from flask import request


TODAY = datetime.utcnow().date()

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


def is_empty(string):
    return 0 if string == "" or string is None else string


def is_bot():
    return request.headers.get('User-Agent') == 'gobot-covid19/3.0'


def is_not_bot():
    return not request.headers.get('User-Agent') == 'gobot-covid19/2.0'


def gen(number):
    return f"{int(number):,}".replace(",", ".")


DAERAH = {
        "aceh": "Aceh",
        "bali": "Bali",
        "banten": "Banten",
        "bengkulu": "Bengkulu",
        "gorontalo": "Gorontalo",
        "jakarta": "DKI Jakarta",
        "jambi": "Jambi",
        "jateng": "Jawa Tengah",
        "jatim": "Jawa Timur",
        "kalbar": "Kalimantan Barat",
        "kalsel": "Kalimantan Selatan",
        "kalteng": "Kalimantan Tengah",
        "kaltim": "Kalimantan Timur",
        "kaltara": "Kalimantan Utara",
        "kep-bangka": "Kepulauan Bangka Belitung",
        "kepri": "Kepulauan Riau",
        "lampung": "Lampung",
        "maluku": "Maluku",
        "maluku-utara": "Maluku Utara",
        "kalbar": "Kalimantan Barat",
        "sulbar": "Sulawesi Barat",
        "sulut": "Sulawesi Utara",
        "sulsel": "Sulawesi Selatan",
        "gorontalo": "Gorontalo",
        "ntb": "Nusa Tenggara Barat",
        "ntt": "Nusa Tenggara Timur",
        "papua": "Papua",
        "papua-barat": "Papua Barat",
        "riau": "Riau",
        "sulbar": "Sulawesi Barat",
        "sulsel": "Sulawesi Selatan",
        "sulteng": "Sulawesi Tengah",
        "sultra": "Sulawesi Tenggara",
        "sulut": "Sulawesi Utara",
        "sumbar": "Sumatera Barat",
        "sumsel": "Sumatera Selatan",
        "sumut": "Sumatera Utara",
        "yogya": "Daerah Istimewa Yogyakarta"
    }


HOTLINE = [
    {
        "kota": "Kabupaten Bandung",
        "callCenter": [],
        "hotline": ["082118219287"]
    },
    {
        "kota": "Kabupaten Bandung Barat",
        "callCenter": [],
        "hotline": ["089522434611"]
    },
    {
        "kota": "Kabupaten Bekasi",
        "callCenter": ["112", "119"],
        "hotline": ["02189910039", "08111139927", "085283980119"]
    },
    {
        "kota": "Kabupaten Bogor",
        "callCenter": ["112", "119"],
        "hotline": []
    },
    {
        "kota": "Kabupaten Ciamis",
        "callCenter": ["119"],
        "hotline": ["081394489808", "085314993901"]
    },
    {
        "kota": "Kabupaten Cianjur",
        "callCenter": [],
        "hotline": ["085321161119"]
    },
    {
        "kota": "Kabupaten Cirebon",
        "callCenter": [],
        "hotline": ["02318800119", "081998800119"]
    },
    {
        "kota": "Kabupaten Garut",
        "callCenter": ["119"],
        "hotline": ["02622802800", "08112040119"]
    },
    {
        "kota": "Kabupaten Indramayu",
        "callCenter": [],
        "hotline": ["08111333314"]
    },
    {
        "kota": "Kabupaten Karawang",
        "callCenter": ["119", "08999700119"],
        "hotline": ["085282537355", "082125569259", "081574371120"]
    },
    {
        "kota": "Kabupaten Kuningan",
        "callCenter": [],
        "hotline": ["081388284346"]
    },
    {
        "kota": "Kabupaten Majalengka",
        "callCenter": ["112"],
        "hotline": ["0233829111", "081324849727"]
    }
    ,
    {
        "kota": "Kabupaten Pangandaran",
        "callCenter": ["119"],
        "hotline": ["085320643695"]
    }
    ,
    {
        "kota": "Kabupaten Purwakarta",
        "callCenter": ["112"],
        "hotline": ["081909514472"]
    }
    ,
    {
        "kota": "Kabupaten Subang",
        "callCenter": [],
        "hotline": ["081322916001", "082115467455"]
    }
    ,
    {
        "kota": "Kabupaten Sukabumi",
        "callCenter": ["112"],
        "hotline": ["02666243816", "081213583160"]
    }
    ,
    {
        "kota": "Kabupaten Sumedang",
        "callCenter": ["119"],
        "hotline": []
    }
    ,
    {
        "kota": "Kabupaten Tasikmalaya",
        "callCenter": ["119"],
        "hotline": ["08122066396"]
    }
    ,
    {
        "kota": "Kota Bandung",
        "callCenter": ["112", "119"],
        "hotline": []
    }
    ,
    {
        "kota": "Kota Banjar",
        "callCenter": ["112"],
        "hotline": ["085223344119", "082120370313", "085353089099"]
    }
    ,
    {
        "kota": "Kota Bekasi",
        "callCenter": ["119"],
        "hotline": ["081380027110"]
    }
    ,
    {
        "kota": "Kota Bogor",
        "callCenter": ["112"],
        "hotline": ["02518363335", "08111116093"]
    }
    ,
    {
        "kota": "Kota Cimahi",
        "callCenter": [],
        "hotline": ["08122126257", "081221423039"]
    }
    ,
    {
        "kota": "Kota Cirebon",
        "callCenter": ["112"],
        "hotline": ["0231237303"]
    }
    ,
    {
        "kota": "Kota Depok",
        "callCenter": ["112", "119"],
        "hotline": []
    }
    ,
    {
        "kota": "Kota Sukabumi",
        "callCenter": [],
        "hotline": ["08001000119"]
    }
    ,
    {
        "kota": "Kota Tasikmalaya",
        "callCenter": [],
        "hotline": ["08112133119"]
    }
]
