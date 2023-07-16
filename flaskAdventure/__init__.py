import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Add the database to the app
    # from . import AdventureGptBE
    # gpt = AdventureGptBE

    # Add a blueprint for the AdventureGame and the main index route
    from . import game
    app.register_blueprint(game.bp)
    app.add_url_rule('/', endpoint='index')

    return app