from flask import Flask

from .game import Game

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'reallyreallysecret'

    from .main import main as main_blueprint
    from .distance_api import api
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api)

    return app
