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
        elif len(first_pos) != 2:
            return '', HTTPStatus.BAD_REQUEST
        elif 'x' not in first_pos or 'y' not in first_pos:
            x = None
            if 'east' in first_pos:
                x = first_pos['east']
            elif 'west' in first_pos:
                x = -first_pos['west']
            if x is None:
                return '', HTTPStatus.BAD_REQUEST
            y = None
            if 'north' in first_pos:
                y = first_pos['north']
            elif 'south' in first_pos:
                y = -first_pos['south']
            if y is None:
                return '', HTTPStatus.BAD_REQUEST
            first_pos = {
                'x': x,
                'y': y
            }
            

        if type(second_pos) == str and robot_re.fullmatch(second_pos):
            robot_id2 = int(second_pos[6:])
            if robot_id2 in robot_pos:
                second_pos = robot_pos[robot_id2]
            else:
                return '', 424
        elif len(second_pos) != 2:
            return '', HTTPStatus.BAD_REQUEST
        elif 'x' not in second_pos or 'y' not in second_pos:
            x = None
            if 'east' in second_pos:
                x = second_pos['east']
            elif 'west' in second_pos:
                x = -second_pos['west']
            if x is None:
                return '', HTTPStatus.BAD_REQUEST
            y = None
            if 'north' in second_pos:
                y = second_pos['north']
            elif 'south' in second_pos:
                y = -second_pos['south']
            if y is None:
                return '', HTTPStatus.BAD_REQUEST
            second_pos = {
                'x': x,
                'y': y
            }

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
        pos = body['position']
        if len(pos) != 2:
            return '', HTTPStatus.BAD_REQUEST
        elif 'x' not in pos or 'y' not in pos:
            x = None
            if 'east' in pos:
                x = pos['east']
            elif 'west' in pos:
                x = -pos['west']
            if x is None:
                return '', HTTPStatus.BAD_REQUEST
            y = None
            if 'north' in pos:
                y = pos['north']
            elif 'south' in pos:
                y = -pos['south']
            if y is None:
                return '', HTTPStatus.BAD_REQUEST
            pos = {
                'x': x,
                'y': y
            }

        _update_robot_pos(robot_id, pos)
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
        k = body['k'] if 'k' in body else 1
        if tree == None:
            nearest_robot = []
        else:
            _, idxes = tree.query((ref_position['x'], ref_position['y']), k=k)
            if k == 1:
                nearest_robot = [sorted_robot_ids[idxes]]
            else:
                nearest_robot = [sorted_robot_ids[idx] for idx in idxes if idx < len(sorted_robot_ids)]
        return jsonify(robot_ids=nearest_robot), HTTPStatus.OK
    except:
        return '', HTTPStatus.BAD_REQUEST

@app.route("/alien/<object_dna>/report", methods=['POST'])
def report_object():
    pass

@app.route("/alien/{object_dna}/position", methods=['GET'])
def find_object_position():
    pass

@app.route("/closestpair", methods=['GET'])
def find_closest_robot():
    if not nearest_dist or nearest_dist == float('inf'):
        return '', 424
    return jsonify(distance=nearest_dist), HTTPStatus.OK