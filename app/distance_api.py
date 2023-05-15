import json

from flask import Blueprint, request, jsonify, abort
from geopy.distance import distance

USERS = [
    "IckyBathroom",
    "ProfuseGod"
]

api = Blueprint("api", __name__)

@api.route("/update_location", methods=["POST"])
def update_location():
    data = request.get_json(force=True)
    print(data)
    name = data["name"]
    if name not in USERS:
        abort(403)
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    coords = (latitude, longitude)
    with open(f"{name}.txt", "w") as f:
        f.write(json.dumps(coords))
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@api.route("/distance", methods=["GET"])
def get_distance():
    coords = []
    for user in USERS:
        with open(f"{user}.txt", 'r') as f:
            coords.append(tuple(json.loads(f.read().strip())))
    return jsonify(distance(*coords).km)