from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from models import db
from routes import bp as routes_bp  # Import the Blueprint

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitbit.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register the blueprint
    app.register_blueprint(routes_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5005)
