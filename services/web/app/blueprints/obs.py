from datetime import datetime

import flask
from flask import request, jsonify
from flask_socketio import emit

last_done = None
last_play = None

obs_bp = flask.Blueprint('obs', __name__)


@obs_bp.route('/live-status', methods=['GET', 'POST'])
def live_status():
    global last_done, last_play
    if request.method == 'POST':

        if "action" in request.args.to_dict().keys():
            request_args_dict = request.args.to_dict()
            request_vals_dict = request.values.to_dict()
            action_ = request_args_dict["action"]
            if "addr" in request_vals_dict.keys():
                addr_ = request_vals_dict.get('addr')

                if not addr_.startswith("unix") and not addr_ == "127.0.0.1":
                    stream_name = ""
                    if "name" in request_vals_dict.keys():
                        stream_name = request_vals_dict.get('name')

                    if action_ == "done":
                        last_done = datetime.now().timestamp()
                    if action_ == "play":
                        last_play = datetime.now().timestamp()
                    emit("my event", {
                        "action": action_,
                        "stream": stream_name,
                        "last_done": last_done if last_done is not None else 0,
                        "last_play": last_play if last_play is not None else 0, "addr": addr_})

        return jsonify({})
    else:
        request_vals_dict = request.values.to_dict()
        print(request_vals_dict)
        return jsonify(request_vals_dict)
