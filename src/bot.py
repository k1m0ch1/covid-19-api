from datetime import datetime, timedelta
import dateutil

from src.helper import gen

# flake8: noqa

def summary(data):
    return f"*Global Cases*\n\nConfirmed: {gen(data['confirmed'])} \n" \
        f"Deaths: {gen(data['deaths'])} \nRecovered: {gen(data['recovered'])}"


def countries(data):
    waktu = dateutil.parser.parse(data['last_updated']) + timedelta(hours=7)
    waktu = datetime.strftime(waktu, "%d %b %Y %H:%M")

    footer = f"Last Updated: {waktu}\nData Source: https://git.io/Jvoxz"
    confirmed, deaths, recovered = 0, 0, 0
    c_diff, d_diff, r_diff = 0, 0, 0
    header = f"*{data['diff'][0]['countryRegion']}*"
    for item in data['origin']:
        confirmed += int(item['confirmed'])
        deaths += int(item['deaths'])
        recovered += int(item['recovered'])
    for item in data['diff']:
        c_diff += int(item['confirmed'])
        d_diff += int(item['deaths'])
        r_diff += int(item['recovered'])
    Confirmed = f"Confirmed: {gen(confirmed)} *(+{gen(confirmed - c_diff)})*"
    Deaths = f"Deaths: {gen(deaths)} *(+{gen(deaths - d_diff)})*"
    Recovered = f"Recovered: {gen(recovered)} *(+{gen(recovered - r_diff)})*"
    return f"{header}\n\n{Confirmed}\n{Deaths}\n{Recovered}\n\n{footer}"


def id(data):
    waktu = dateutil.parser.parse(data['metadata']['last_updated']) + timedelta(hours=7)
    waktu = datetime.strftime(waktu, "%d %b %Y %H:%M")

    return "*Indonesia*\n\n" \
        f"Terkonfirmasi: {gen(data['confirmed']['value'])} *(+{gen(data['confirmed']['diff'])})*\n" \
        f"Meninggal: {gen(data['deaths']['value'])} *(+{gen(data['deaths']['diff'])})*\n" \
        f"Sembuh: {gen(data['recovered']['value'])} *(+{gen(data['recovered']['diff'])})*\n" \
        f"Dalam Perawatan: {gen(data['active_care']['value'])} *(+{gen(data['active_care']['diff'])})*\n\n" \
        f"Update Terakhir {waktu}\nSumber data https://kawalcovid19.id"


def province(data):
    waktu = dateutil.parser.parse(data['metadata']['source_date']) + timedelta(hours=7)
    waktu = datetime.strftime(waktu, "%d %b %Y %H:%M")

    result = f"*{data['metadata']['province']}*"

    sembuh_diff = f"*(+{gen(data['total_sembuh']['diff'])})*" if data['total_sembuh']['diff'] > 0 else ""
    sembuh = f"Sembuh: {gen(data['total_sembuh']['value'])} {sembuh_diff}"

    positif_diff = f"*(+{gen(data['total_positif']['diff'])})*" if data['total_positif']['diff'] > 0 else ""
    positif = f"Positif: {gen(data['total_positif']['value'])} {positif_diff}"

    meninggal_diff = f"*(+{gen(data['total_meninggal']['diff'])})*" if data['total_meninggal']['diff'] > 0 else ""
    meninggal = f"Meninggal: {gen(data['total_meninggal']['value'])} {meninggal_diff}"

    footer = f"Update Terakhir {waktu}\nSumber data : {data['metadata']['source']}"

    return f"{result}\n\n{sembuh}\n{positif}\n{meninggal}\n\n{footer}"


def province_list(data):
    header = "*List Provinsi yang tersedia*"
    footer = "Contoh Penggunaan : *!covid id papua*"
    result = ""
    for index, value in enumerate(data):
        if index%8 == 0 :
            result +="\n\n"
        result += f"{value}, "
    return f"{header}{result}\n\n{footer}"


def news(data):
    result = "*Top Headline News*\n\n"
    for item in data:
        result += f"{item['title']}\n{item['url']}\n\n"
    return result + "Cermat dalam mengamati berita dan hindari hoaks\nBantu kami di https://git.io/JvPbJ ❤️"


def hotline(data):
    header = "*List Hotline*\n\n"
    result = ""
    for index, item in enumerate(data):
        result += f"*{item['kota']}*\n"
        result += "Call Center: "
        for row in item['callCenter']:
            result += f"{row}, "
        result += f"\nHotline: "
        for row in item['hotline']:
            result += f"{row}, "
        result += "\n\n"
    return result

