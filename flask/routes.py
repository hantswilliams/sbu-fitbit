from flask import Blueprint, redirect, request, session, url_for, render_template, jsonify
import requests
from datetime import datetime, timedelta
from models import db, FitbitUser
import os
from utils import get_activity_options  # Import the utility function

# Fitbit API credentials
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "https://fitbit-6m5burcysa-uc.a.run.app/callback"
REVOKE_TOKEN_URL = "https://api.fitbit.com/oauth2/revoke"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"
AUTHORIZATION_BASE_URL = "https://www.fitbit.com/oauth2/authorize"

# Define the Blueprint for routes
bp = Blueprint('routes', __name__)

@bp.route("/")
def index():
    return render_template('index.html')

@bp.route("/login")
def login():
    authorization_url = f"{AUTHORIZATION_BASE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=activity heartrate sleep"
    return redirect(authorization_url)

@bp.route("/callback")
def callback():
    code = request.args.get('code')
    token_response = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data={
        'client_id': CLIENT_ID,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code': code
    })
    token_json = token_response.json()

    # Calculate the expiration time
    expires_at = datetime.utcnow() + timedelta(seconds=token_json['expires_in'])

    # Save tokens and user_id in the database
    user = FitbitUser(
        user_id=token_json['user_id'],
        access_token=token_json['access_token'],
        refresh_token=token_json['refresh_token'],
        expires_at=expires_at
    )

    # Add the user to the database and overwrite the existing user if it already exists
    if FitbitUser.query.filter_by(user_id=token_json['user_id']).first():
        db.session.query(FitbitUser).filter_by(user_id=token_json['user_id']).delete()
        db.session.commit()

    db.session.add(user)
    db.session.commit()

    session['user_id'] = token_json['user_id']
    return redirect(url_for('routes.dashboard'))

@bp.route("/signout")
def signout():
    user_id = session.get('user_id')
    if user_id:
        user = FitbitUser.query.filter_by(user_id=user_id).first()
        if user:
            # Revoke the token by making a POST request to Fitbit's revocation endpoint
            revoke_response = requests.post(REVOKE_TOKEN_URL, data={
                'token': user.access_token,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            })

            # Check if the token was successfully revoked
            if revoke_response.status_code == 200:
                print("Token successfully revoked.")
            else:
                print("Failed to revoke token. Response:", revoke_response.json())

            # Delete the user from the database
            db.session.delete(user)
            db.session.commit()

    # Clear the session data
    session.clear()
    # Redirect the user to the home page
    return redirect(url_for('routes.index'))

@bp.route("/dashboard")
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('routes.index'))

    user = FitbitUser.query.filter_by(user_id=user_id).first()
    if not user:
        return redirect(url_for('routes.index'))

    activity_options = get_activity_options()  # Get activity options
    print(activity_options)

    return render_template('dashboard.html', user_id=user_id, activity_options=activity_options)

@bp.route("/get_activity_data", methods=["POST"])
def get_activity_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    user = FitbitUser.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    resource = request.json.get('resource')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')

    if not resource or not start_date or not end_date:
        return jsonify({"error": "Missing required parameters"}), 400

    headers = {'Authorization': f"Bearer {user.access_token}"}

    try:
        url = f'https://api.fitbit.com/1/user/{user.user_id}/activities/{resource}/date/{start_date}/{end_date}.json'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as err:
        print('Error: ', err)
        return jsonify({"error": str(err)}), 500

    return jsonify(data)
