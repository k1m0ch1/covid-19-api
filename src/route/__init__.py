from flask import Flask
from .root import root


def register_route(app: Flask):
    app.register_blueprint(root, url_prefix='/')
