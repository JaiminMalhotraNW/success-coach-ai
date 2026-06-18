import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agents.conversation_agent import get_conversation_agent, SYSTEM_PROMPT
from tools.sheets_client import get_all_students

st.set_page_config(page_title="MentorMate - Success Coach AI", page_icon="🎓")

# --- Fetch Live Student Data ---
# This uses our cached function, so it only pulls from Google Sheets once per hour!
with st.spinner("Loading student database..."):
    STUDENTS = get_all_students()

# --- Session State Initialization ---
if "current_student" not in st.session_state:
    st.session_state.current_student = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Login Portal ---
if not st.session_state.current_student:
    st.title("Welcome to MentorMate 🎓")
    st.subheader("Your AI Academic Success Coach")
    
    if not STUDENTS:
        st.error("Could not load students from Google Sheets. Please check your connection and .env file.")
    else:
        # Create the dynamic dropdown from live Google Sheets data
        student_options = [f"{name} ({uid})" for uid, name in STUDENTS.items()]
        selected_option = st.selectbox("Select your profile to login:", student_options)
        
        if st.button("Login"):
            # Extract ID and Name from the selection (e.g., "Arjun (STU001)")
            # Using rsplit to safely handle names that might contain parentheses
            student_name = selected_option.rsplit(" (", 1)[0]
            student_id = selected_option.rsplit(" (", 1)[1].replace(")", "")
            
            st.session_state.current_student = {"id": student_id, "name": student_name}
            
            # Inject the Welcome Message immediately upon login
            st.session_state.messages = [
                {"role": "assistant", "content": f"Welcome, **{student_name}**! I am MentorMate, your Academic Success Coach. How can I support your learning today?"}
            ]
            st.rerun()

# --- Main Chat Interface ---
else:
    student_id = st.session_state.current_student["id"]
    student_name = st.session_state.current_student["name"]
    
    # Sidebar
    with st.sidebar:
        st.write(f"**Logged in as:** {student_name} ({student_id})")
        if st.button("Logout"):
            st.session_state.current_student = None
            st.session_state.messages = []  # Clear chat history on logout
            st.rerun()

    st.title("MentorMate")
    st.caption("Ask me about your scores, attendance, upcoming exams, or portal features.")

    # 1. Display existing chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 2. Handle new user input
    if prompt := st.chat_input("Ask me anything..."):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 3. Inject SYSTEM_PROMPT and strict Student Context
        dynamic_system_prompt = f"{SYSTEM_PROMPT}\n\nIMPORTANT: You are assisting student {student_name} (ID: {student_id}). Use this ID when fetching records, and address them by their name."
        
        lc_messages = [SystemMessage(content=dynamic_system_prompt)]
        
        # 4. Convert Streamlit history to LangChain format
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            else:
                lc_messages.append(AIMessage(content=msg["content"]))

        # 5. Call the Agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                agent = get_conversation_agent()
                response = agent.invoke({"messages": lc_messages})["messages"][-1].content
                st.markdown(response)
            
        st.session_state.messages.append({"role": "assistant", "content": response})