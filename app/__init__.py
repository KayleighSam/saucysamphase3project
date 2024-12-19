from flask import Flask
from .routes import main_blueprint

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Register blueprint
    app.register_blueprint(main_blueprint)

    return app
