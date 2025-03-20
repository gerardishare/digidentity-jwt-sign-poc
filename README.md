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

## Azure Deployment

### Prerequisites
1. An Azure account with an active subscription
2. A GitHub account with your code repository
3. Azure CLI installed (optional, for local testing)

### Setup Azure Resources

1. Create an Azure App Service:
   - Go to Azure Portal (portal.azure.com)
   - Click "Create a resource"
   - Search for "Web App"
   - Choose "Web App" and click "Create"
   - Fill in the details:
     - Resource Group: Create new or select existing
     - Name: your-app-name (must be unique)
     - Publish: Code
     - Runtime stack: Python 3.8 or higher
     - Operating System: Linux
     - Region: Choose nearest to you
   - Click "Review + create" and then "Create"

2. Configure Application Settings:
   - In your web app, go to "Settings" > "Configuration"
   - Add the following application settings:
     ```
     FLASK_SECRET_KEY=your-secret-key
     DIGIDENTITY_CLIENT_ID=your-client-id
     DIGIDENTITY_CLIENT_SECRET=your-client-secret
     DIGIDENTITY_API_KEY=your-api-key
     FLASK_ENV=preprod  # or 'prod' for production
     CERTIFICATE_CHAIN_PATH=/home/site/wwwroot/config/certificates.pem
     SCM_DO_BUILD_DURING_DEPLOYMENT=true
     WEBSITE_WEBDEPLOY_USE_SCM=false
     ```

### GitHub Actions Setup

1. Create a GitHub Actions workflow file:
   - Create `.github/workflows/azure-deploy.yml` in your repository

2. Add the following content to the file:
   ```yaml
   name: Deploy to Azure
   
   on:
     push:
       branches:
         - main  # or your default branch
   
   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v2
       
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: '3.8'
           
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -r requirements.txt
           
       - name: Upload certificates
         run: |
           mkdir -p config
           echo "${{ secrets.CERTIFICATE_CHAIN }}" > config/certificates.pem
           
       - name: Deploy to Azure
         uses: azure/webapps-deploy@v2
         with:
           app-name: 'your-app-name'  # Replace with your app name
           publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
           package: .
   ```

### Configure GitHub Secrets

1. Get the publish profile:
   - Go to your Azure Web App
   - Click "Get publish profile"
   - Copy the contents

2. Add secrets in GitHub:
   - Go to your GitHub repository
   - Click "Settings" > "Secrets and variables" > "Actions"
   - Add the following secrets:
     - `AZURE_WEBAPP_PUBLISH_PROFILE`: Paste the publish profile content
     - `CERTIFICATE_CHAIN`: Content of your certificates.pem file

### Deploy

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Ready for Azure deployment"
   git push
   ```

2. Monitor deployment:
   - Go to your GitHub repository
   - Click "Actions" tab
   - Watch the deployment progress

### Troubleshooting Deployment

1. Check deployment logs:
   - Go to GitHub Actions tab
   - Click on the latest workflow run
   - Expand the job logs for details

2. Check Azure logs:
   - Go to Azure Portal
   - Navigate to your Web App
   - Click "Log stream" to see live logs
   - Check "App Service logs" for detailed logging

3. Common issues:
   - Certificate path issues: Verify the CERTIFICATE_CHAIN_PATH in Azure configuration
   - Environment variables: Ensure all required variables are set in Azure configuration
   - Python version mismatch: Check the Python version in Azure matches your requirements
   - Dependencies: Make sure all requirements are properly listed in requirements.txt

### Security Notes

- Never commit sensitive data (certificates, keys, credentials) to the repository
- Always use GitHub Secrets for sensitive information
- Regularly rotate your credentials and update the secrets
- Consider using Azure Key Vault for managing secrets in production 