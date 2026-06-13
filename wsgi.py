import sys
import os

# Add project directory to path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Load .env for local development (optional — on PythonAnywhere set env vars
# directly in the WSGI config file under the "Environment variables" section:
#   GMAIL_ADDRESS = your_gmail@gmail.com
#   GMAIL_APP_PASSWORD = your_app_password
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(path, '.env'))
except ImportError:
    pass

from app import app as application
