from services.web.app import create_app
from dotenv import load_dotenv

load_dotenv('.env')

socketio, app = create_app()


if __name__ == '__main__':
    socketio.run(app, port=5005, debug=True, allow_unsafe_werkzeug=True)
