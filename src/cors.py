
from flask_cors import CORS

cors = CORS(resources={r"/maskmap/*": {"origins": "*"}})


def init_app(app):
    cors.init_app(app)
