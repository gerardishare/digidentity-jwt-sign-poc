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

def load_certificates(cert_path):
    """Load certificates from PEM file and return as array of base64 encoded strings."""
    try:
        with open(cert_path, 'r') as f:
            content = f.read()
            # Split on certificate boundaries and filter empty strings
            certs = [cert.strip() for cert in content.split('-----END CERTIFICATE-----')]
            cert_array = []
            for cert in certs:
                if cert:
                    # Add back the END marker that was removed by split
                    cert = cert + '-----END CERTIFICATE-----'
                    # Remove headers/footers and whitespace
                    cert = cert.replace('-----BEGIN CERTIFICATE-----', '') \
                             .replace('-----END CERTIFICATE-----', '') \
                             .strip()
                    # Remove any newlines to get clean base64
                    cert = cert.replace('\n', '')
                    
                    # Validate base64 encoding
                    try:
                        # Test if it's valid base64
                        base64.b64decode(cert)
                        cert_array.append(cert)
                    except Exception as e:
                        logger.error(f"Invalid base64 in certificate: {e}")
                        continue
                        
            if not cert_array:
                logger.error("No valid certificates found in chain")
            else:
                logger.info(f"Successfully loaded {len(cert_array)} certificates")
                
            return cert_array
    except FileNotFoundError:
        logger.error(f"Certificate file not found: {cert_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading certificates: {e}")
        return []

@app.route('/sign', methods=['POST'])
def sign():
    try:
        # Parse JSON from form data
        jwt_header = json.loads(request.form.get('jwt_header'))
        jwt_body = json.loads(request.form.get('jwt_body'))
        
        # Load certificates and add to header
        cert_path = os.getenv('CERTIFICATE_CHAIN_PATH')
        if cert_path is None:
            raise ValueError(
                "CERTIFICATE_CHAIN_PATH environment variable is not set and default path is None"
            )
        if not os.path.exists(cert_path):
            raise FileNotFoundError(
                f"Certificate chain file not found at {cert_path}. "
                "Please copy config/certificates.pem.example to config/certificates.pem "
                "and add your certificate chain."
            )
            
        # Load and validate certificates
        certificates = load_certificates(cert_path)
        if not certificates:
            raise ValueError("No valid certificates found in certificate chain")
            
        # Add certificates to header and ensure proper algorithm
        jwt_header.update({
            'alg': 'RS256',  # Ensure we're using RS256
            'typ': 'JWT',    # Explicitly set JWT type
            'x5c': certificates  # Add certificate chain
        })
        
        logger.info("Certificate chain loaded:")
        logger.info(f"Number of certificates: {len(certificates)}")
        for i, cert in enumerate(certificates):
            logger.info(f"Certificate {i+1} length: {len(cert)}")
            logger.info(f"Certificate {i+1} preview: {cert[:50]}...")
        
        access_token = session.get('access_token')
        api_key = os.getenv('DIGIDENTITY_API_KEY')
        
        def base64url_encode(data):
            """Base64Url-encode data according to JWT spec."""
            if isinstance(data, str):
                data = data.encode('utf-8')
            elif isinstance(data, dict):
                data = json.dumps(data).encode('utf-8')
            
            encoded = base64.urlsafe_b64encode(data).rstrip(b'=')
            return encoded.decode('utf-8')
        
        # Create JWT components
        header_b64 = base64url_encode(jwt_header)
        payload_b64 = base64url_encode(jwt_body)
        signing_input = f"{header_b64}.{payload_b64}"
        
        # Calculate hash using binary data, not string
        calculated_hash = hashlib.sha256(signing_input.encode('utf-8')).hexdigest()
        
        logger.info(f"JWT Components:")
        logger.info(f"Header (decoded): {jwt_header}")
        logger.info(f"Header (base64): {header_b64}")
        logger.info(f"Payload (decoded): {jwt_body}")
        logger.info(f"Payload (base64): {payload_b64}")
        logger.info(f"Signing Input: {signing_input}")
        logger.info(f"Hash: {calculated_hash}")
        
        # Prepare signing request
        url = config.SIGN_ENDPOINT.format(auto_signer_id=os.getenv('DIGIDENTITY_AUTO_SIGNER_ID'))
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Api-Key': api_key,
            'Content-Type': 'application/vnd.api+json'
        }
        data = {
            "data": {
                "type": "sign",
                "attributes": {
                    "hash_to_sign": calculated_hash  # Send base64 encoded binary hash
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
        signature = response_data['data']['attributes']['signature'].replace("\n", "")
        jwt_signature = base64.urlsafe_b64encode(base64.b64decode(signature)).decode().strip("=")
        
        signed_jwt = f"{signing_input}.{jwt_signature}"
        
        logger.info("Final JWT components:")
        logger.info(f"Header part: {header_b64}")
        logger.info(f"Payload part: {payload_b64}")
        logger.info(f"Signature part: {signature}")
        logger.info(f"Final JWT: {signed_jwt}")
        
        return render_template('result.html', signed_jwt=signed_jwt)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    app.run(debug=True) 