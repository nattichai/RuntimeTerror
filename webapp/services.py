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

        if type(first_pos) == str and robot_re.fullmatch(first_pos):
            first_pos = robot_pos[int(first_pos[6:])]

        if type(second_pos) == str and robot_re.fullmatch(second_pos):
            second_pos = robot_pos[int(second_pos[6:])]

        metric = body['metric'] if 'metric' in body else 'euclidean'
        if metric == 'euclidean':
            distance = _get_euclidean_distance(first_pos, second_pos)
        elif metric == 'manhattan':
            distance = _get_manhattan_distance(first_pos, second_pos)

        return jsonify(distance=distance), HTTPStatus.OK
    except:
        return '', HTTPStatus.BAD_REQUEST

def _get_euclidean_distance(p1, p2):
    return ((p1['x'] - p2['x']) ** 2 + (p1['y'] - p2['y']) ** 2) ** 0.5

def _get_manhattan_distance(p1, p2):
    return abs(p1['x'] - p2['x']) + abs(p1['y'] - p2['y'])

@app.route("/robot/<robot_id>/position", methods=['PUT'])
def update_robot_position(robot_id):
    robot_id = int(robot_id)

    body = request.get_json()
    robot_pos[robot_id] = body['position']
    return '', HTTPStatus.NO_CONTENT

@app.route("/robot/<robot_id>/position", methods=['GET'])
def get_robot_position(robot_id):
    robot_id = int(robot_id)

    if robot_id in robot_pos:
        return jsonify(position=robot_pos[robot_id]), HTTPStatus.OK
    else:
        return '', HTTPStatus.NOT_FOUND

@app.route("/nearest", methods=['POST'])
def find_nearest_robot():
    body = request.get_json()

    ref_position = body['ref_position']
    nearest_robot = []
    min_dist = float('inf')
    for robot_id in robot_pos:
        dist = _get_euclidean_distance(robot_pos[robot_id], ref_position)
        if dist < min_dist:
            min_dist = dist
            nearest_robot = [robot_id]
    return jsonify(robot_ids=nearest_robot), HTTPStatus.OK