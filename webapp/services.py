import re
from http import HTTPStatus
from flask import Flask, jsonify, request

app = Flask(__name__)

robot_re = re.compile(r"^robot#([1-9][0-9]*)")
robot_pos = {}

@app.route("/distance", methods=['POST'])
def find_distance():
    body = request.get_json()
    try:
        first_pos = body['first_pos']
        second_pos = body['second_pos']
        print(first_pos, second_pos, type(first_pos), type(second_pos))
        if type(first_pos) == str and robot_re.fullmatch(first_pos):
            first_pos = robot_pos[first_pos[6:]]
        if type(second_pos) == str and robot_re.fullmatch(second_pos):
            second_pos = robot_pos[second_pos[6:]]
        return jsonify(distance=_get_euclidean_distance(first_pos, second_pos)), HTTPStatus.OK
    except:
        return '', HTTPStatus.BAD_REQUEST

def _get_euclidean_distance(p1, p2):
    return ((p1['x'] - p2['x']) ** 2 + (p1['y'] - p2['y']) ** 2) ** 0.5

@app.route("/robot/<robot_id>/position", methods=['PUT'])
def update_robot_position(robot_id):
    body = request.get_json()
    robot_pos[robot_id] = body['position']
    return '', HTTPStatus.NO_CONTENT

@app.route("/robot/<robot_id>/position", methods=['GET'])
def get_robot_position(robot_id):
    if robot_id in robot_pos:
        return jsonify(position=robot_pos[robot_id]), HTTPStatus.OK
    else:
        return '', HTTPStatus.NOT_FOUND