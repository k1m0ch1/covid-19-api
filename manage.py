import fire
import os

from src.wsgi import app


def run_scrapper():
    print("run scrapper")


def clear_cache():
    print("clear cache")


def run_web():
    app.run(host='0.0.0.0', port=5001, debug=True)


def run_web_prod():
    """Run web application in production"""

    _execvp([
        "gunicorn", "--config", "python:src.gunicorn_cfg", "src.wsgi:app"
    ])


def test():
    print("unittest")


def _execvp(args):
    os.execvp(args[0], args)


if __name__ == '__main__':
    fire.Fire()
