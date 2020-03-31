from os import environ

_ = environ.get


DBSTRING = _('DBSTRING',
             'postgresql://untitled-web:untitled-web@localhost/covid19api')
WEBDRIVER = _('WEBDRIVER', './chromedriver')

DATASET_ALL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv" # noqa
NEWSAPI_KEY = _('NEWSAPI_KEY', "xxxxxxxxxx")

NEWSAPI_HOST = _('NEWSAPI_HOST', "http://newsapi.org/v2/top-headlines")
sLIMITER = 5
