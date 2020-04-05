from base64 import b64decode, b64encode
from wand.image import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from src import config, helper, crawler
from src.db import session
from src.models import Attachment

import time
import math


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
    save_attachment = Attachment(
        key="graph.harian",
        attachment=encoded_data
    )

    session.add(save_attachment)

    print("--[+] Start Seed Province")
    # seed the province
    for province in helper.DAERAH:
        print(f"--[+] Seed {province}")
        nothing = crawler.odi_api(province) # noqa
    print("[*] Seeder Done")
