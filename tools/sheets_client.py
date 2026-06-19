import os
import json
import gspread
import streamlit as st
from dotenv import load_dotenv
from langchain_core.tools import tool

# Load environment variables from .env
load_dotenv()

SHEET_URL = "https://docs.google.com/spreadsheets/d/1vKn-9LCCcBPjfcFUgEzAWBGpsjzCJtPvrln05rR1Ht0/edit?gid=911132763#gid=911132763"

def get_worksheet_data(worksheet_name: str):
    """Internal helper to fetch all records from a specific Google Sheet tab using Service Account."""
    try:
        # Load Service Account credentials from .env
        creds_string = os.getenv("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_string)
        
        # Authenticate with Service Account
        gc = gspread.service_account_from_dict(creds_dict)
        
        # Fetch data
        return gc.open_by_url(SHEET_URL).worksheet(worksheet_name).get_all_records()
    except Exception as e:
        print(f"Google Sheets Error: {e}")
        return []

@st.cache_data(ttl=3600) 
def get_all_students():
    """Fetches unique students from the 'roster' sheet to populate the UI dropdown."""
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
    Look up detailed exam performance for a specific student. 
    Use this to retrieve a list of subject-wise exam scores, including 
    the student's marks, the maximum possible marks, and the exam date. 
    Ideal for answering queries about academic progress or specific test results.
    """
    data = get_worksheet_data("exam_scores")
    records = [r for r in data if str(r.get('student_id', '')).strip().upper() == student_id.upper()]
    return f"Exam Scores: {records}" if records else "No exam records found."

@tool
def get_student_attendance(student_id: str) -> str:
    """
    Look up the weekly attendance history for a specific student.
    Use this to see how many classes were scheduled vs. attended and 
    calculate overall attendance percentage. Essential for providing 
    feedback on attendance patterns or addressing concerns about absenteeism.
    """
    data = get_worksheet_data("attendance")
    records = [r for r in data if str(r.get('student_id', '')).strip().upper() == student_id.upper()]
    return f"Attendance Records: {records}" if records else "No attendance records found."

@tool
def get_exam_schedule(student_id: str) -> str:
    """
    Look up the upcoming exam schedule for a specific student.
    Use this to provide details on upcoming tests, including subjects, 
    scheduled dates, and exam formats. Use this when the student asks 
    about 'when is my next exam' or 'what tests are coming up'.
    """
    data = get_worksheet_data("exam_schedule")
    records = [r for r in data if str(r.get('student_id', '')).strip().upper() == student_id.upper()]
    return f"Upcoming Exams: {records}" if records else "No upcoming exams found."