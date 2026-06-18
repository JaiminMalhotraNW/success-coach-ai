from langgraph.prebuilt import create_react_agent
from config.llm import get_llm
from tools.sheets_client import get_student_scores, get_student_attendance, get_exam_schedule

def get_conversation_agent():
    llm = get_llm()
    # Now the agent has access to all three tools
    tools = [get_student_scores, get_student_attendance, get_exam_schedule]
    return create_react_agent(llm, tools)