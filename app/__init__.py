from flask import Flask
from flask_socketio import SocketIO

from .game import Game

socketio = SocketIO()


def create_app(debug=True):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'reallyreallysecret'

    from .main import main_blueprint
    from .distance_api import api
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api)

    socketio.init_app(app)
    return app
