from flask import Blueprint, jsonify, request
from src.cache import cache
import time
from sqlalchemy import or_
from datetime import datetime, timedelta

from src.db import session
from src.models import User, Place, Story
from src.helper import is_bot


maskmap = Blueprint('maskmap', __name__)


@maskmap.before_request
def before_request(request):
    if is_bot():
        return jsonify(message="Not Found"), 404


@maskmap.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add(
        'Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response


@maskmap.route('/places', methods=['POST'])
@cache.cached(timeout=50)
def queryPlaces():
    body = request.get_json()
    places = session.query(Place) \
        .filter(or_(Place.name.like(f'%{body.get("name")}%'),
                    Place.lng == body.get("long"),
                    Place.lat == body.get("lat"))
                ) \
        .all()

    if len(places) == 0:
        return jsonify(message="Not Found"), 404

    if places is not None:
        return jsonify([_placeDict(place) for place in places]), 200


@maskmap.route('/places')
@cache.cached(timeout=50)
def getAllPlaces():
    diff = (datetime.utcnow() - timedelta(days=2))
    if request.args.get("days"):
        diff = (datetime.utcnow() -
                timedelta(days=int(request.args.get("days"))))
    if request.args.get("hours"):
        diff = (datetime.utcnow() -
                timedelta(days=int(request.args.get("hours"))))

    places = session.query(Place).all()

    if len(places) == 0:
        return jsonify(message="Not Found"), 404

    if places is not None:
        return jsonify([_placeDict(place) for place in places]), 200


@maskmap.route('/stories')
@cache.cached(timeout=50)
def getAllStories():
    stories = session.query(Story).all()

    if len(stories) == 0:
        return jsonify(message="Not Found"), 404

    if stories is not None:
        return jsonify([_storyDict(story) for story in stories]), 200


@maskmap.route('/story/<story_id>')
def getStory(story_id):
    story = session.query(Story).get(story_id)
    if story is not None:
        return jsonify(_storyDict(story)), 200
    return jsonify(message="Not Found"), 404


@maskmap.route('/place/<place_id>')
def getPlace(place_id):
    place = session.query(Place).get(place_id)
    if place is not None:
        return jsonify(_placeDict(place)), 200
    return jsonify(message="Not Found"), 404


@maskmap.route('/user/<user_id>')
def getUser(user_id):
    user = session.query(User).get(user_id)
    if user is not None:
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "birthdate": time.mktime(user.birthdate.timetuple()),
            "phone": user.phone,
            "created": time.mktime(user.created.timetuple())
        }), 200
    return jsonify(message="Not Found"), 404


@maskmap.route('/user', methods=['POST'])
def handleUserCreated():
    body = request.get_json()
    new_user = User(
        name=body.get("name"),
        email=body.get("email"),
        birthdate=body.get("birthdate"),
        phone=body.get("phone"),
    )

    session.add(new_user)
    session.flush()

    return jsonify({'id': new_user.id})


@maskmap.route('/place', methods=['POST'])
def handlePlaceCreated():
    body = request.get_json()
    new_place = Place(
        name=body.get("name"),
        lng=body.get("long"),
        lat=body.get("lat"),
        description=body.get("description"),
    )

    session.add(new_place)
    session.flush()

    return jsonify({'id': new_place.id})


@maskmap.route('/stories', methods=['POST'])
def handleStoriesCreated():
    body = request.get_json()
    new_story = Story(
        place_id=body.get("place_id"),
        user_id=body.get("user_id"),
        availability=body.get("availability"),
        num=body.get("num"),
        price=body.get("price"),
        validity=body.get("validity")
    )

    session.add(new_story)
    session.flush()

    return jsonify({'id': new_story.id})


def _placeDict(place):
    return {
        "id": place.id,
        "name": place.name,
        "lat": place.lat,
        "long": place.lng,
        "description": place.description,
        "created": place.created.isoformat(),
        "availability": _groupSort(place.story),
        "story": [_storyDict(row) for row in place.story]
    }


def _storyDict(story):
    return {
        "id": story.id,
        "place_id": story.place_id,
        "user_id": story.user_id,
        "availability": story.availability,
        "num": story.num,
        "price": story.price,
        "validity": story.validity,
        "created": time.mktime(story.created.timetuple())
    }


def _groupSort(story):
    data = {}
    for row in story:
        if row.validity not in data:
            data[row.validity] = {}

        if row.availability not in data[row.validity]:
            data[row.validity][row.availability] = 0

        data[row.validity][row.availability] += 1
    return data
