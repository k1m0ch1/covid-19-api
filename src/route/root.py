from flask import Blueprint, jsonify
from src import data

root = Blueprint('root', __name__)


@root.route('/')
@root.route('/summary')
def index():
    return jsonify(data.case()), 200


@root.route('/all')
def all_data():
    return jsonify(data.case()), 200


@root.route('/<country_id>')
def country(country_id: str):
    return jsonify(data.case()), 200


