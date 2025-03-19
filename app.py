from flask import Flask, render_template, request, redirect, session, url_for
import requests
from dotenv import load_dotenv
import os
import base64
from config.config import load_config
import logging
import json
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
config = load_config()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Required for session management

# GitHub OAuth configuration
DIGIDENTITY_CLIENT_ID = os.getenv('DIGIDENTITY_CLIENT_ID')
DIGIDENTITY_CLIENT_SECRET = os.getenv('DIGIDENTITY_CLIENT_SECRET')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    # Client Credentials Flow
    credentials = f"{DIGIDENTITY_CLIENT_ID}:{DIGIDENTITY_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    url = config.TOKEN_ENDPOINT
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Accept': 'application/json'
    }
    data = {
        'grant_type': 'client_credentials',
        #'scope': '1e78xm7pls3c9p1e'
    }
    
    logger.info(f"Authentication Request:")
    logger.info(f"URL: {url}")
    logger.info(f"Headers: {json.dumps(headers, indent=2)}")
    logger.info(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, headers=headers, data=data)
    
    logger.info(f"Authentication Response:")
    logger.info(f"Status Code: {response.status_code}")
    logger.info(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
    logger.info(f"Response Body: {json.dumps(response.json() if response.ok else response.text, indent=2)}")
    
    if response.ok:
        access_token = response.json().get('access_token')
        session['access_token'] = access_token
        return {'success': True}
    return {'success': False, 'error': 'Authentication failed'}, 401

@app.route('/sign', methods=['POST'])
def sign():
    try:
        # Parse JSON from form data
        jwt_header = json.loads(request.form.get('jwt_header'))
        jwt_body = json.loads(request.form.get('jwt_body'))
        access_token = session.get('access_token')
        api_key = os.getenv('DIGIDENTITY_API_KEY')
        
        def base64url_encode(data):
            """Base64Url-encode data according to JWT spec."""
            encoded = base64.urlsafe_b64encode(json.dumps(data).encode())
            return encoded.rstrip(b'=').decode('utf-8')
        
        # Create JWT components
        header_b64 = base64url_encode(jwt_header)
        payload_b64 = base64url_encode(jwt_body)
        signing_input = f"{header_b64}.{payload_b64}"
        
        # Calculate hash of the signing input
        calculated_hash = hashlib.sha256(signing_input.encode()).hexdigest()
        
        logger.info(f"JWT Components:")
        logger.info(f"Header (decoded): {jwt_header}")
        logger.info(f"Header (base64): {header_b64}")
        logger.info(f"Payload (decoded): {jwt_body}")
        logger.info(f"Payload (base64): {payload_b64}")
        logger.info(f"Signing Input: {signing_input}")
        logger.info(f"Hash: {calculated_hash}")
        
        # Prepare signing request
        url = config.SIGN_ENDPOINT
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Api-Key': api_key,
            'Content-Type': 'application/vnd.api+json'
        }
        data = {
            "data": {
                "type": "sign",
                "attributes": {
                    "hash_to_sign": calculated_hash
                }
            }
        }
        
        logger.info(f"Signing Request:")
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {json.dumps(headers, indent=2)}")
        logger.info(f"Data: {json.dumps(data, indent=2)}")
        # Send signing request
      
        response = requests.post(url, headers=headers, json=data)

        logger.info(f"Signing Response:")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        logger.info(f"Response Body: {json.dumps(response.json() if response.ok else response.text, indent=2)}")
        
        if not response.ok:
            logger.error(f"Signing failed: {response.text}")
            return {'error': 'Signing failed', 'details': response.text}, response.status_code
        
        # Extract signature and create final JWT
        response_data = response.json()
        signature = response_data['data']['attributes']['signature']
        signed_jwt = f"{signing_input}.{signature}"
        
        logger.info(f"Final JWT: {signed_jwt}")
        
        return render_template('result.html', signed_jwt=signed_jwt)
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {e}")
        return {'error': 'Invalid JSON format'}, 400
    except KeyError as e:
        logger.error(f"Missing required field in response: {e}")
        return {'error': 'Invalid response format from signing service'}, 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    app.run(debug=True) 