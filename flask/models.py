from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FitbitUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
