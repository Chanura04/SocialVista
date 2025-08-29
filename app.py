# app.py

import os, glob
import uuid
from flask import Flask
from dotenv import load_dotenv

# Import the Blueprints you will create
from blueprints.auth.routes import auth_bp
from blueprints.x_platform.routes import twitter_bp
from blueprints.dashboard.routes import dashboard_bp
from blueprints.api_details.routes import api_details_bp

load_dotenv()

# We can put some of the functions from app.py here as they are general purpose
def clear_session_files():
    for file in glob.glob("flask_session/*"):
        os.remove(file)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "default-secret-key") # Use an environment variable for a stronger key

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(twitter_bp, url_prefix='/x_platform')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(api_details_bp, url_prefix='/api_details')

    # Add other configurations if needed
    app.config["SESSION_RESET_TOKEN"] = str(uuid.uuid4())
    clear_session_files()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)