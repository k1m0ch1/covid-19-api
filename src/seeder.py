from base64 import b64decode, b64encode
from wand.image import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

from src import config, helper
from src.models import Attachment, Status

import time
import math
import requests


def seed():
    # seed the statistic graph
    print("[*] Start Seeder")
    time.sleep(2)
    print("--[+] Seed Graph")
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(config.CHROMEDRIVER, options=options)
    driver.get(config.STATISTIK_URL)
    time.sleep(15)
    driver.set_window_size(1600, 1200)
    image = driver.find_element_by_tag_name('body')
    ActionChains(driver).move_to_element(image).perform()
    src_base64 = driver.get_screenshot_as_base64()
    scr_png = b64decode(src_base64)
    scr_img = Image(blob=scr_png)

    x = image.location["x"]
    y = image.location["y"] + 510
    w = image.size["width"] - 720
    h = image.size["height"] - 757
    scr_img.crop(
        left=math.floor(x),
        top=math.floor(y),
        width=math.ceil(w),
        height=math.ceil(h),
    )

    encoded_data = b64encode(scr_img.make_blob()).decode("utf-8")
    print("--[+] Save Graph to DB")
    with helper.transaction() as tx:
        save_attachment = Attachment(
            key="graph.harian",
            attachment=encoded_data
        )

        tx.add(save_attachment)

        print("--[+] Start Seed Province")
        # seed the province
        for province in helper.DAERAH:
            print(f"--[+] Seed {province}")
            nothing = odi_api(province) # noqa
        print("[*] Seeder Done")


ODI_API = 'https://indonesia-covid-19.mathdro.id/api/provinsi'


def odi_api(state):
    DAERAH = helper.DAERAH
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

    with helper.transaction() as tx:
        get_state = tx.query(Status) \
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
        with helper.transaction() as tx:
            new_status = Status(
                confirmed=hasil["kasusPosi"],
                deaths=hasil["kasusMeni"],
                recovered=hasil["kasusSemb"],
                active_care=0,
                country_id=f"id.{state}",
                created=datetime.utcnow(),
                updated=datetime.utcnow()
            )
            tx.add(new_status)
            result["metadata"]["source_date"] = \
                datetime.utcnow().isoformat()

    result["total_sembuh"]["value"] = hasil["kasusSemb"]
    result["total_positif"]["value"] = hasil["kasusPosi"]
    result["total_meninggal"]["value"] = hasil["kasusMeni"]

    return result
