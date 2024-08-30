from flask import Flask, redirect, request, session, url_for, render_template
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Fitbit API credentials
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "https://fitbit-6m5burcysa-uc.a.run.app/callback"
API_BASE_URL = "https://api.fitbit.com/1/user/-/"

# OAuth 2.0 endpoints
AUTHORIZATION_BASE_URL = "https://www.fitbit.com/oauth2/authorize"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    authorization_url = f"{AUTHORIZATION_BASE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=activity heartrate sleep"
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    code = request.args.get('code')
    token_response = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data={
        'client_id': CLIENT_ID,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code': code
    })
    token_json = token_response.json()
    session['access_token'] = token_json['access_token']
    session['user_id'] = token_json['user_id']     ## also save the user id
    return redirect(url_for('dashboard'))

@app.route("/signout")
def signout():
    # Clear the session data
    session.clear()
    # Redirect the user to the home page
    return redirect(url_for('index'))

@app.route("/dashboard")
def dashboard():
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    try:
        profile_response = requests.get(f'https://api.fitbit.com/1/user/{session["user_id"]}/profile.json', headers=headers)
        profile_response.raise_for_status()
        data = profile_response.json()
        print('Data retrieved for user: ', data)
    except requests.exceptions.HTTPError as err:
        print('Error: ', err)
        data = None

    return render_template('dashboard.html', data=data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5005)
