from services.web.main import app, socketio

if __name__ == "__main__":
    socketio.run(app, port=5005, debug=True, allow_unsafe_werkzeug=True)
