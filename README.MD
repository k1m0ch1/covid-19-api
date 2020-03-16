# Coronavirus Disease 19 API Tracker

This is just a simple API tracker for covid-19 latest information for recovered, confirmed and deaths cases. The main purpose of this repo is for bot announcement to whatsapp, telegram and discord about latest cases of covid-19


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

# Development
This repo is still on development and
## Requirement
1. Python 3.7
2. pipenv/ pip
3. venv/ virtualenv


## Next to do :
- deploy to server for public use
- add new endpoint for each countries
- add new endoint `/confirmed` `/deaths` and `/recovered`
- bot discord
- bot whatsapp
- bot telegram
- news crawler from reliable resource

This repo is inspired from @mathdroid repo https://github.com/mathdroid/covid-19-api
