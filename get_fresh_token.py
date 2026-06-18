import os
import json
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

# The permissions we need
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets', 
    'https://www.googleapis.com/auth/drive'
]

def generate_new_token():
    print("Loading credentials from .env...")
    load_dotenv()
    
    creds_string = os.getenv("GOOGLE_CREDENTIALS")
    if not creds_string:
        print("❌ Could not find GOOGLE_CREDENTIALS in .env!")
        return

    creds_dict = json.loads(creds_string)
    
    print("Opening your browser to authenticate with Google...")
    # This pops open the browser for you to click "Allow"
    flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
    creds = flow.run_local_server(port=0)

    # We pack the fresh credentials into a dictionary
    token_dict = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    print("\n" + "="*60)
    print("✅ AUTHENTICATION SUCCESSFUL!")
    print("Copy the entire line below and replace the GOOGLE_TOKEN line in your .env file:\n")
    
    # This prints the EXACT string you need, perfectly formatted!
    print(f"GOOGLE_TOKEN='{json.dumps(token_dict)}'")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate_new_token()