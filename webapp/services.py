import re
import closest_pairs
from scipy import spatial
from http import HTTPStatus
from flask import Flask, jsonify, request

app = Flask(__name__)

robot_re = re.compile(r"^robot#([1-9][0-9]*)")
robot_pos = {}
sorted_robot_ids = None
tree = None
nearest_dist = None

@app.route("/distance", methods=['POST'])
def find_distance():
    try:
        body = request.get_json()
    
        first_pos = body['first_pos']
        second_pos = body['second_pos']

        if type(first_pos) == str and robot_re.fullmatch(first_pos):
            robot_id1 = int(first_pos[6:])
            if robot_id1 in robot_pos:
                first_pos = robot_pos[robot_id1]
            else:
                return '', 424

        if type(second_pos) == str and robot_re.fullmatch(second_pos):
            robot_id2 = int(second_pos[6:])
            if robot_id2 in robot_pos:
                second_pos = robot_pos[robot_id2]
            else:
                return '', 424

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
    try:
        robot_id = int(robot_id)

        body = request.get_json()
        _update_robot_pos(robot_id, body['position'])
        return '', HTTPStatus.NO_CONTENT
    except:
        return '', HTTPStatus.BAD_REQUEST

def _update_robot_pos(robot_id, pos):
    global tree, sorted_robot_ids, nearest_dist

    robot_pos[robot_id] = pos
    sorted_robot_ids = sorted(robot_pos.keys())
    data = [(x[1]['x'], x[1]['y']) for x in sorted(robot_pos.items())]
    tree = spatial.KDTree(data)
    nearest_dist = min(tree.query(data, k=2)[0][:, 1])

@app.route("/robot/<robot_id>/position", methods=['GET'])
def get_robot_position(robot_id):
    try:
        robot_id = int(robot_id)

        if robot_id in robot_pos:
            return jsonify(position=robot_pos[robot_id]), HTTPStatus.OK
        else:
            return '', HTTPStatus.NOT_FOUND
    except:
        return '', HTTPStatus.NOT_FOUND

@app.route("/nearest", methods=['POST'])
def find_nearest_robot():
    try:
        body = request.get_json()

        ref_position = body['ref_position']
        if tree == None:
            nearest_robot = []
        else:
            _, idx = tree.query((ref_position['x'], ref_position['y']))
            nearest_robot = [sorted_robot_ids[idx]]
        return jsonify(robot_ids=nearest_robot), HTTPStatus.OK
    except:
        return '', HTTPStatus.BAD_REQUEST

@app.route("/closestpair", methods=['GET'])
def find_closest_robot():
    if not nearest_dist or nearest_dist == float('inf'):
        return '', 424
    return jsonify(distance=nearest_dist), HTTPStatus.OK