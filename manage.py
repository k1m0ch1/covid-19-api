import fire

from src.wsgi import app


def run_scrapper():
    print("run scrapper")


def clear_cache():
    print("clear cache")


def run_web():
    app.run(host='0.0.0.0', port=5001, debug=True)


def test():
    print("unittest")


if __name__ == '__main__':
    fire.Fire()
