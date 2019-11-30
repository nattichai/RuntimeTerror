from http import HTTPStatus
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/distance", methods=['POST'])
def find_distance():
    body = request.get_json()
    first_pos = body['first_pos']
    second_pos = body['second_pos']
    return jsonify(distance=_get_distance(first_pos, second_pos)), HTTPStatus.OK

def _get_distance(p1, p2):
    return ((p1['x'] - p2['x']) ** 2 + (p1['y'] - p2['y']) ** 2) ** 0.5