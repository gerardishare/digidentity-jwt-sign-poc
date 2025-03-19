# JWT Signing with Digidentity

A simple web application that allows you to sign JWTs using the Digidentity API. The application uses OAuth2 client credentials flow for authentication and supports both preproduction and production environments. The application is preconfigured to use [iSHARE JWT]() structure.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd github-search
```

2. Create and activate a virtual environment:

**Windows:**
```bash
# Create venv
python -m venv venv

# Activate venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your credentials:
```
FLASK_SECRET_KEY=your-secret-key
DIGIDENTITY_CLIENT_ID=your-client-id
DIGIDENTITY_CLIENT_SECRET=your-client-secret
DIGIDENTITY_API_KEY=your-api-key
FLASK_ENV=preprod  # or 'prod' for production
```

## Running the Application

1. Ensure your virtual environment is activated (you should see `(venv)` in your terminal)
2. Start the Flask application:
```bash
python app.py
```
3. Open your web browser and navigate to: `http://localhost:5000`

## Usage

1. The application shows two text areas for JWT header and body with default values
2. Click "Authenticate with Digidentity" to obtain an access token using client credentials flow
3. After successful authentication, you can modify the JWT header and body as needed
4. Click "Sign JWT" to send the signing request to Digidentity
5. The signed JWT will be displayed on the results page

## Environment Configuration

The application supports two environments:
- Preproduction (`FLASK_ENV=preprod`)
- Production (`FLASK_ENV=prod`)

API endpoints for each environment are configured in:
- `config/preprod.py` - Preproduction endpoints
- `config/prod.py` - Production endpoints

## Project Structure
```
project_root/
├── .env                # Environment variables (not in repo)
├── .gitignore         # Git ignore rules
├── README.md          # This documentation
├── requirements.txt   # Python dependencies
├── app.py            # Main application file
├── config/           # Configuration files
│   ├── __init__.py
│   ├── config.py     # Configuration loader
│   ├── preprod.py    # Preproduction settings
│   └── prod.py       # Production settings
│   └── certificates.pem.example # Example template for certificates
├── static/           # Static files
│   └── style.css     # CSS styles
└── templates/        # HTML templates
    ├── index.html    # Main page
    └── result.html   # Results page
```

## Development Notes

### Virtual Environment Management

To deactivate the virtual environment when you're done:
```bash
deactivate
```

To remove the virtual environment (if needed):
```bash
# Windows
rmdir /s /q venv

# macOS/Linux
rm -rf venv
```

To recreate the virtual environment:
```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

## Troubleshooting

If you encounter issues:
1. Check the console logs for detailed API interaction information
2. Verify your credentials in the `.env` file
3. Ensure you're using the correct environment setting
4. Validate the JWT header and body JSON format
5. Make sure your virtual environment is activated
6. Try recreating the virtual environment if dependencies aren't working 

## Configuration

### Certificates
The application requires a certificate chain file for JWT signing. To set up:

1. Copy the example certificate file:
   ```bash
   cp config/certificates.pem.example config/certificates.pem
   ```
2. Replace the contents with your actual certificate chain in PEM format
   - Start with your leaf certificate
   - Follow with any intermediate certificates
   - End with the root certificate

Configuration options:
- Environment variable: `CERTIFICATE_CHAIN_PATH`
  - Example: `export CERTIFICATE_CHAIN_PATH=/path/to/your/certificates.pem`

Note: The certificate file is excluded from version control for security reasons. Make sure to properly manage your certificates outside the repository. 