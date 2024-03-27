from flask import request, redirect, url_for, requests
from app import *

app = Flask("Google login app")
app.secret_key = ("Secret key")


@app.route('/login/google/callback')
def google_callback():
    # Exchange authorization code for access token
    auth_code = request.args.get('code')
    token_url = 'https://oauth2.googleapis.com/token'
    token_params = {
        'code': auth_code,
        'client_id': "32079113759-868616kq5dqlob3dl4i75vh3kqb9cfen.apps.googleusercontent.com",
        'client_secret': "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",
        'redirect_uri': 'http://localhost:5000',
        'grant_type': 'authorization_code'
    }
    token_response = requests.post(token_url, data=token_params)

    if token_response.status_code == 200:
        access_token = token_response.json().get('access_token')

        user_info_url = 'https://openidconnect.googleapis.com/v1/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code == 200:
            user_info = user_info_response.json()

            email = user_info.get('email')
            user = User.query.filter_by(email=email).first()

            if user:
                login_user(user)
                return redirect(url_for('profile.html'))
            else:
                return redirect(url_for('registration.html'))
        else:

            return "Failed to fetch user information from Google"
    else:
        return "Failed to exchange authorization code for access token"
