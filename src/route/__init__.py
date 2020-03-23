from flask import Flask
from .root import root
from .maskmap import maskmap
from .indonesia import indonesia


def register_route(app: Flask):
    app.register_blueprint(root, url_prefix='/')
    app.register_blueprint(maskmap, url_prefix='/maskmap')
    app.register_blueprint(indonesia, url_prefix='/id')
