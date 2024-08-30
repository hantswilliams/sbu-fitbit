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
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    profile_response = requests.get(API_BASE_URL + 'profile.json', headers=headers)
    data = profile_response.json()
    print('Data retrieved for user: ', data)
    return render_template('dashboard.html', data=data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5005)
