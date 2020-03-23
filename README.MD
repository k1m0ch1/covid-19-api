# Coronavirus Disease 19 API Tracker

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/k1m0ch1/covid-19-api)
![GitHub repo size](https://img.shields.io/github/repo-size/k1m0ch1/covid-19-api)
![GitHub last commit](https://img.shields.io/github/last-commit/k1m0ch1/covid-19-api)
![GitHub stars](https://img.shields.io/github/stars/k1m0ch1/covid-19-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/k1m0ch1/covid-19-api)
![GitHub forks](https://img.shields.io/github/forks/k1m0ch1/covid-19-api)
![GitHub issues](https://img.shields.io/github/issues/k1m0ch1/covid-19-api)
![GitHub watchers](https://img.shields.io/github/watchers/k1m0ch1/covid-19-api)
![Twitter](https://img.shields.io/twitter/follow/bukanyahya?style=social)

This is just a simple API tracker for covid-19 latest information for recovered, confirmed and deaths cases. The main purpose of this repo is for bot announcement to whatsapp, telegram and discord about latest cases of covid-19.

you can try the api here [https://covid19-api.yggdrasil.id/](https://covid19-api.yggdrasil.id/) ![Website](https://img.shields.io/website?down_message=offline&up_message=online&url=https://covid19-api.yggdrasil.id/) thanks for @habibiefaried for helping the server
or [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

# Bot Whatsapp
(WARNING: This is only available with Bahasa Language, need some help for translation)
This bot is for covid-19 information purpose by automatically answer for available data, by using `!covid <command>`, here is the available command :
1. status
This will return information about current global case, example output
```
Confirmed: xx
Deaths: xx
Recovered: xx
```
2. id
This will return information about current indonesia corona case, example output
```
Terkonfirmasi: xx
Meninggal: xx
Sembuh: xx
Dalam Perawatan: xx

Update Terakhir:
2020-03-17T07:01:01+00:00
```
3. id info
This will return basic information about corona in indonesia
4. ping
The bot will response "pong"
5. halo, hello, help
The introduction and list of available command
## Requirement
Docker
## Installation
run this command
```
docker run --restart on-failure --name gobot-covid k1m0ch1/gobot-covid
```
The QR Code will be available in terminal for more less than 10 second, if timeout you need to run the first command again
after the QR Code is succesfully scanned I prefer to run the container in the background by stop the container first with `Ctrl+C` and then run the container again with command `docker start gobot-covid`

### For advance usage
- Session store
This feature will enable to store the session for the later use, by adding the argument as the file name for sesion for example
```
docker run --restart on-failure --name gobot-covid k1m0ch1/gobot-covid MyPhoneNumber
```
the file `MyPhoneNumber.go` will be stored at `./session` folder

the folder `session` in the container at path `/go/src/github.com/k1m0ch1/covid-19-api/session` so you can use `-v` parameter to put the session file in the localhost

here is the complete parameter
```
docker run -v ~/session:/go/src/github.com/k1m0ch1/covid-19-api/session x--restart on-failure --name gobot-covid k1m0ch1/gobot-covid MyPhoneNumber
```

# Endpoint

## Get latest information about confirmed, deaths and recovered
```
GET /
```

```
{"Confirmed":167447,"Deaths":6440,"Recovered":76034}
```
## Get each countries confirmed, deaths, and recovered cases
```
GET /confirmed
```

```
[
    ...,
    {
        "confirmed": 14991,
        "countryRegion": "Iran",
        "lastUpdate": "2020-03-16T14:38:45",
        "latitude": "32.4279",
        "longitude": "53.6880",
        "provinceState": null
    }
    ...,
]
```
same as result with endpoint `GET /deaths` and `GET /recovered`
## Get latest information about all country cases status
```
GET /all
```
```
[
    ...,
    {
        "Confirmed": xx,
        "CountryRegion": "CountryName",
        "Deaths": xx,
        "LastUpdate": <timestamp iso 8601 format>,
        "Latitude": "xx.x",
        "Longitude": "-xx.x",
        "ProvinceState": "State" or null,
        "Recovered": xx
    },
    ...
]
```
## List of available countries
```
GET /countries
```
## List of available countries detail cases
```
GET /countries/<alpha2-country-code>
```
```
GET /countries/us
```
```
[
    ...,
    {
        "confirmed": 557,
        "countryRegion": "US",
        "deaths": 7,
        "lastUpdate": "2020-03-16T23:53:03",
        "latitude": "36.1162",
        "longitude": "-119.6816",
        "provinceState": "California",
        "recovered": 6
    },
    ...,
    {
        "summary": {
            "confirmed": 4632,
            "deaths": 85,
            "recovered": 17
        }
    }
    ...,
]
```
if the country only have a single data, the summary data will not exist

## List of available news
```
GET /news
```
get the latest top headlines about corona virus,
the news is get from `NewsAPI.org` see there for available news

## List of available news in specific countries
```
GET /news/<alpha2-country-code>
```
get the latest top headlines about corona virus in specific countries,
the news is get from `NewsAPI.org` see there for available news

# Docker
You can use docker by pull
```
docker run --name covid-19-api -p 5001:5001 -d docker.pkg.github.com/k1m0ch1/covid-19-api/covid-19-api:latest run
```
or
```
docker run --name covid-19-api -p 5000:5000 -d docker.pkg.github.com/k1m0ch1/covid-19-api/covid-19-api:latest run_web_prod
```

# Development
This repo is still on development and feel free to contribute.
## Requirement
1. Python 3.7
2. pipenv/ pip
3. venv/ virtualenv

## Running on development
```
pipenv run python manage.py run
```

## Running on production
```
pipenv run python manage.py run_web_prod
or
gunicorn --config python:src.gunicorn_cfg src.wsgi:app
```

## Next to do :
- ~~deploy to server for public use~~ deployed to [https://covid19-api.yggdrasil.id/](https://covid19-api.yggdrasil.id/) Thanks @habibiefaried
- ~~add new endpoint for each countries~~ referrence from @mathdroid
- ~~add new endoint `/confirmed` `/deaths` and `/recovered`~~
- bot discord
- ~~bot whatsapp~~
- bot telegram
- news crawler from reliable resource

## Bot Whatsapp to do :
- ~~session is stored into specific volume, so can be used later~~
- ~~prevent the whatsapp spam~~
- make much more simple way to run this bot for cross platform
- ~~for command `id` need to add development of the number before and after~~
- for command `id` add a linear graph better get from https://kawalcovid19.blob.core.windows.net/viz/statistik_harian.html
- ~~add a new command `jabar` scrape from https://pikobar.jabarprov.go.id/~~
- add a new command `jkt` scrape from http://corona.jakarta.go.id/
- add `id info` for much more detail information
- add `id hotline` for much more detail information

# Referrence
- This repo is inspired from @mathdroid repo https://github.com/mathdroid/covid-19-api, some of the similiar is credited to @mathdroid
- Global case data is parsed from [2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)
