from flask_limiter import Limiter

limiter = Limiter()


def init_app(app):
    limiter.init_app(app)
