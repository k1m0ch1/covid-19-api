from flask import Flask
from .route import register_route
from src import cache, db, limit, cors


def create_app():
    app = Flask(__name__)

    register_route(app)
    cache.init_app(app)
    db.init_app(app)
    limit.init_app(app)
    cors.init_app(app)

    return app
