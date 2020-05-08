import random
import string

from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from markupsafe import escape

app = Flask(__name__)
CORS(app)

db = {}


@app.route("/")
def welcome():
    return "Welcome to Anon-Feed API! Try visiting /session/create/"


@app.route("/session/")
@app.route("/session/create/")
def create_session():
    session_id = get_session_id()
    db[session_id] = []
    return jsonify({"session_id": session_id})


@app.route("/session/list/")
def get_all_session_ids():
    return jsonify(list(db.keys()))


@app.route("/session/<session_id>/")
def fetch_session(session_id):
    safe_session_id = escape(session_id)
    if safe_session_id in db:
        return jsonify(db[safe_session_id])
    else:
        return send_error("E001")


@app.route("/session/<session_id>/feedback/add/")
def add_feedback(session_id):
    safe_session_id = escape(session_id)
    if safe_session_id not in db:
        return send_error("E001")

    feedback_message = request.args.get("msg")
    if feedback_message is None:
        return send_error("E002")

    feedback_message = escape(feedback_message)

    if len(feedback_message) > 500:
        return send_error("E003")

    db[safe_session_id].append(feedback_message)

    return jsonify({"success": True})


def get_session_id():
    session_id = get_random_str(6)
    while session_id in db:
        session_id = get_random_str(6)
    return session_id


def get_random_str(size):
    possible_chars = string.ascii_letters + string.digits
    random_str_list = random.choices(possible_chars, k=size)
    return "".join(random_str_list)


def send_error(error_code):
    error_list = {
        "E001": ("Session ID not found", 404),
        "E002": ("No feedback message found", 400),
        "E003": (
            "Feedback message has crossed the maximum limit of 512 characters",
            400,
        ),
    }
    return jsonify({"error": error_list[error_code][0]}), error_list[error_code][1]
