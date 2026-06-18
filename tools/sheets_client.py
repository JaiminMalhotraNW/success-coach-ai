import os
import gspread
from langchain_core.tools import tool

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vKn-9LCCcBPjfcFUgEzAWBGpsjzCJtPvrln05rR1Ht0/edit?gid=911132763#gid=911132763"

def get_worksheet_data(worksheet_name: str):
    """Internal helper to fetch all records from a specific Google Sheet tab."""
    try:
        gc = gspread.oauth(credentials_filename=CLIENT_SECRET_PATH, authorized_user_filename=TOKEN_PATH)
        return gc.open_by_url(SHEET_URL).worksheet(worksheet_name).get_all_records()
    except Exception as e:
        return f"Error: {e}"

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