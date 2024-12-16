from flask import Flask
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)


@app.route('/initiate_payment', methods=['POST'])
def initiate_payment():
    partyA = input('Enter phone')
    try:
        access_token = get_access_token()
        if access_token:
            payload = {
                "BusinessShortCode": "174379",
                "Password": "Safaricom999!*!",
                "Timestamp": "20220314072700",
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",
                "PartyA": partyA,
                "PartyB": "174379",
                "PhoneNumber": partyA,
                "CallBackURL": "YOUR_CALLBACK_URL",
                "AccountReference": "Test",
                "TransactionDesc": "Test Payment"
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.post(
                'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        else:
            return 'Access token not found'
    except requests.RequestException as e:
        return f'Error: {e}'


def get_access_token():
    consumer_key = 'PKreMGJ7wTszUSnPOnZJcdPQEUbBcNDcCYu9IOqvqdYHrIbr'
    consumer_secret = '3UOS9ruBBQqK5qJrSxSKdos8JzdMXU1kAZEuUOUuDByn2LBXeODVyNqJGUVRXJT0'
    mpesa_auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    try:
        data = requests.get(mpesa_auth_url, auth=HTTPBasicAuth(
            consumer_key, consumer_secret))
        data.raise_for_status()
        dict_data = data.json()
        print(dict_data.get('access_token'))
        return dict_data.get('access_token')
    except requests.RequestException as e:
        print(f'Error: {e}')
        return None
