import os
import json
import gspread
from dotenv import load_dotenv

load_dotenv()

def test_service_account():
    print("1. Loading .env configuration...")
    creds_string = os.getenv("GOOGLE_CREDENTIALS")
    
    if not creds_string:
        print("❌ FAILED: GOOGLE_CREDENTIALS not found in .env")
        return

    try:
        print("2. Parsing JSON...")
        creds_dict = json.loads(creds_string)
        
        print("3. Authenticating with Google Service Account...")
        gc = gspread.service_account_from_dict(creds_dict)
        
        print("4. Accessing Spreadsheet...")
        SHEET_URL = "https://docs.google.com/spreadsheets/d/1vKn-9LCCcBPjfcFUgEzAWBGpsjzCJtPvrln05rR1Ht0/edit?gid=911132763#gid=911132763"
        sheet = gc.open_by_url(SHEET_URL)
        
        # Test reading from the 'roster' tab
        worksheet = sheet.worksheet("roster")
        data = worksheet.get_all_records()
        
        print(f"✅ SUCCESS! Connected and read {len(data)} rows from 'roster'.")
        print(f"Sample data: {data[0] if data else 'Empty'}")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print("👉 TIP: Ensure your .env string contains the entire JSON with double quotes and newlines.")

if __name__ == "__main__":
    test_service_account()