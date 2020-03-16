from flask import Flask
from .route import register_route
from src import cache


def create_app():
    app = Flask(__name__)

    register_route(app)
    cache.init_app(app)

    return app
