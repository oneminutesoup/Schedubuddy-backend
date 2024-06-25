import flask, json
from flask import request, jsonify, abort
from flask_cors import CORS
from flask_compress import Compress
from query import query
from scheduler import sched_gen

qe = query.QueryExecutor()
sf = sched_gen.ScheduleFactory()

app = flask.Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = 'Content-Type'
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def api_root():
    return json.dumps({'success':True}), 200, {'ContentType':'app/json'} 

@app.route("/api/v1/terms", methods=['GET'])
def api_terms():
    return jsonify(qe.get_terms())

@app.route("/api/v1/courses/", methods=['GET'])
def api_courses():
    args = request.args
    if "term" not in args:
        return
    term_id = int(args["term"])
    return jsonify(qe.get_term_courses(term_id))

@app.route("/api/v1/classes/", methods=['GET'])
def api_classes():
    args = request.args
    if "term" not in args or "course" not in args:
        return
    term_id, course_ids = int(args["term"]), args["course"]
    return jsonify(qe.get_course_classes(term_id, course_ids))

@app.route("/api/v1/gen-schedules/", methods=['GET', 'POST'])
def api_gen_schedules():
    args = request.args
    required_args = ("term", "courses")
    for required_arg in required_args:
        if required_arg not in args:
            return
    term_id, course_id_list = int(args["term"]), args["courses"]
    prefs = None
    if "prefs" in args:
        prefs = args["prefs"]
    else:
        prefs = [args["evening"], args["online"], args["start"], args["consec"], args["limit"], args["blacklist"]]
    response = jsonify(qe.get_schedules(term_id, course_id_list, prefs, sf))
    return response

@app.route("/api/v1/rooms/", methods=['GET', 'POST'])
def api_rooms():
    args = request.args
    if "term" not in args:
        return
    term_id = int(args["term"])
    return jsonify(qe.get_term_rooms(term_id))

@app.route("/api/v1/room-sched/", methods=['GET', 'POST'])
def api_room_sched():
    args = request.args
    required_args = ("term", "room")
    for required_arg in required_args:
        if required_arg not in args:
            return
    return jsonify(qe.get_room_classes(args["term"], args["room"]))

@app.route("/api/all-rooms-open/", methods=['GET', 'POST'])
def api_all_avail_rooms():
    # ensure good request
    args = request.args
    if not (args.keys() >= {"term","weekday","starttime","endtime"}):
        return jsonify({"message":"provide all required query params!"}), 400
    # Get all distinct classes
    distinct_rooms = qe.get_avaliable_rooms(args["term"], args["weekday"], args["starttime"], args["endtime"])
    return jsonify({"available_rooms": distinct_rooms }), 200

Compress(app)
if __name__ == "__main__":
    app.run()
