from flask import Flask
from .root import root
from .maskmap import maskmap


def register_route(app: Flask):
    app.register_blueprint(root, url_prefix='/')
    app.register_blueprint(maskmap, url_prefix='/maskmap')
