import os
import json
import gspread
import streamlit as st
from dotenv import load_dotenv
from langchain_core.tools import tool
from google.oauth2.credentials import Credentials

# Load environment variables from .env
load_dotenv()

SHEET_URL = "https://docs.google.com/spreadsheets/d/1vKn-9LCCcBPjfcFUgEzAWBGpsjzCJtPvrln05rR1Ht0/edit?gid=911132763#gid=911132763"

def get_worksheet_data(worksheet_name: str):
    """Internal helper to fetch all records from a specific Google Sheet tab."""
    try:
        # 1. Grab the token string from .env
        token_string = os.getenv("GOOGLE_TOKEN")
        if not token_string:
            return []
            
        # 2. Convert to dictionary
        token_dict = json.loads(token_string)
        
        # 3. Authenticate using the bulletproof method from our test
        creds = Credentials.from_authorized_user_info(token_dict)
        gc = gspread.authorize(creds)
        
        # 4. Fetch the data
        return gc.open_by_url(SHEET_URL).worksheet(worksheet_name).get_all_records()
    except Exception as e:
        print(f"Google Sheets Error: {e}")
        return []

@st.cache_data(ttl=3600) 
def get_all_students():
    """Fetches unique students from the 'roster' sheet to populate the UI dropdown."""
    # CHANGED: Target the existing 'roster' tab
    data = get_worksheet_data("roster")
    students_dict = {}
    
    if isinstance(data, list):
        for row in data:
            s_id = str(row.get('student_id', '')).strip().upper()
            s_name = str(row.get('name', s_id)).strip() 
            if s_id:
                students_dict[s_id] = s_name

    return students_dict

@tool
def get_student_scores(student_id: str) -> str:
    """
    Retrieves academic performance data for a student.
    Returns a list of dictionaries containing subject name, score, max_score, and date.
    Use this when a student asks about their exam grades or academic progress.
    """
    data = get_worksheet_data("exam_scores")
    records = [r for r in data if str(r.get('student_id', '')).strip().upper() == student_id.upper()]
    return f"Exam Scores: {records}" if records else "No exam records found."

@tool
def get_student_attendance(student_id: str) -> str:
    """
    Retrieves weekly attendance statistics for a student.
    Returns a list of records showing weeks scheduled vs attended and attendance percentage.
    Use this to identify attendance patterns or when a student asks 'how is my attendance?'.
    """
    data = get_worksheet_data("attendance")
    records = [r for r in data if str(r.get('student_id', '')).strip().upper() == student_id.upper()]
    return f"Attendance Records: {records}" if records else "No attendance records found."

@tool
def get_exam_schedule(student_id: str) -> str:
    """
    Retrieves the upcoming exam schedule for a specific student.
    Returns a list of upcoming subjects, dates, and exam types.
    Use this when a student asks about their upcoming tests or deadlines.
    """
    data = get_worksheet_data("exam_schedule")
    records = [r for r in data if str(r.get('student_id', '')).strip().upper() == student_id.upper()]
    return f"Upcoming Exams: {records}" if records else "No upcoming exams found."