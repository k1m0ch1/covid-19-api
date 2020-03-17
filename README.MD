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

you can try the api here [https;//covid-19api.heroku.com/](https;//covid-19api.heroku.com/) ![Website](https://img.shields.io/website?down_message=offline&up_message=online&url=https%3A%2F%2Fcovid-19api.herokuapp.com%2F)
or [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)


# Endpoint

## Get latest information about confirmed, deaths and recovered
```
GET /
```

```
{"Confirmed":167447,"Deaths":6440,"Recovered":76034}
```
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

# Docker
You can use docker by pull
```
docker run --name covid-19-api -p 5001:5001 -d docker.pkg.github.com/k1m0ch1/covid-19-api/covid-19-api:latest run
```
or
```
docker run --name covid-19-api -p 8000:8000 -d docker.pkg.github.com/k1m0ch1/covid-19-api/covid-19-api:latest run_web_prod
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
- ~~deploy to server for public use~~ deployed to [https;//covid-19api.heroku.com/](https;//covid-19api.heroku.com/)
- add new endpoint for each countries
- add new endoint `/confirmed` `/deaths` and `/recovered`
- bot discord
- bot whatsapp
- bot telegram
- news crawler from reliable resource

# Referrence
- This repo is inspired from @mathdroid repo https://github.com/mathdroid/covid-19-api, some of the similiar is credited to @mathdroid
- Global case data is parsed from [2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)
