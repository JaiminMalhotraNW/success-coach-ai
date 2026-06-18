import os
import gspread
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from mem0 import Memory

# Load environment variables from .env
load_dotenv()

def test_openai():
    print("🔄 Testing OpenAI API...")
    try:
        llm = ChatOpenAI(
            model="gpt-5.4-mini-2026-03-17", 
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        response = llm.invoke([HumanMessage(content="Ping")])
        if response.content:
            print("✅ OpenAI API: Working successfully!")
            return True
    except Exception as e:
        print(f"❌ OpenAI API Failed: {e}")
    return False

def test_mem0():
    print("\n🔄 Testing Mem0 API...")
    try:
        # Check if API key exists in environment
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            print("❌ Mem0 API Failed: MEM0_API_KEY not found in .env file.")
            return False
            
        config = {"vector_store": {"provider": "openai"}}
        memory = Memory.from_config(config)
        # Attempt a lightweight retrieval or basic instantiation check
        if memory:
            print("✅ Mem0 API: Client initialized successfully!")
            return True
    except Exception as e:
        print(f"❌ Mem0 API Failed: {e}")
    return False

def test_google_sheets():
    print("\n🔄 Testing Google Sheets Connection...")
    try:
        # Check if credentials file exists
        if not os.path.exists('credentials.json'):
            print("❌ Google Sheets Failed: 'credentials.json' file missing from project root.")
            return False
            
        gc = gspread.service_account(filename='credentials.json')
        # Open the sheet by the exact name
        spreadsheet = gc.open("Success Coach AI Data")
        worksheet = spreadsheet.worksheet("Roster")
        first_row = worksheet.row_values(1)
        
        print(f"✅ Google Sheets: Connected successfully! Found sheet columns: {first_row}")
        return True
    except Exception as e:
        print(f"❌ Google Sheets Failed: {e}")
        print("💡 Tip: Make sure you shared your Google Sheet with the email address inside credentials.json!")
    return False

if __name__ == "__main__":
    print("🚀 Starting Success Coach AI Diagnostic Check...\n" + "="*50)
    openai_ok = test_openai()
    mem0_ok = test_mem0()
    sheets_ok = test_google_sheets()
    print("="*50 + "\n🏁 Diagnostic Complete.")