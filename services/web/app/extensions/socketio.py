from flask_socketio import SocketIO, send

socketio = SocketIO()


@socketio.on('my event')
def handle_message(data):
    print(data)
    send(data)


@socketio.on('json')
def handle_json(json_data):
    print("JSON")
    send(json_data, json=True)
