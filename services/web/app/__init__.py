import os

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from services.web.app.extensions.db import db
from services.web.app.extensions.bootstrap import bootstrap
from services.web.app.extensions.csrf import csrf
from services.web.app.extensions.socketio import socketio

from services.web.app.blueprints.general import general_bp
from services.web.app.blueprints.auth import auth_bp
from services.web.app.blueprints.servers import servers_bp
from services.web.app.blueprints.obs import obs_bp


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://localuser:localpass@127.0.0.1:3306/localdb'
    # serve locally for faster and offline development
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    # set default button style and size, will be overwritten by macro parameters
    app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
    app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'

    # set default icon title of table actions
    app.config['BOOTSTRAP_TABLE_VIEW_TITLE'] = 'Read'
    app.config['BOOTSTRAP_TABLE_EDIT_TITLE'] = 'Update'
    app.config['BOOTSTRAP_TABLE_DELETE_TITLE'] = 'Remove'
    app.config['BOOTSTRAP_TABLE_NEW_TITLE'] = 'Create'
    app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'darkly'

    app.config["TIMEZONE_NAME"] = os.getenv('TIMEZONE_NAME')
    app.config["2FA_REQUIRED"] = False
    db.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)

    app.register_blueprint(servers_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(general_bp)
    app.register_blueprint(obs_bp)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from services.web.app.models import LiveStatus, Users

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return Users.query.get(int(user_id))

    with app.app_context():
        db.drop_all()
        db.create_all()

    Migrate(app, db)

    return socketio, app
