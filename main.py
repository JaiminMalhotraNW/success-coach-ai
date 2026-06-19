import os
import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agents.conversation_agent import get_conversation_agent, SYSTEM_PROMPT
from tools.sheets_client import get_all_students
from mem0 import MemoryClient
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Initialize Mem0 Client
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
if MEM0_API_KEY:
    memory_client = MemoryClient(api_key=MEM0_API_KEY)
else:
    memory_client = None
    st.warning("Mem0 API Key is missing. Memory saving will be disabled.")

# --- Page Config ---
st.set_page_config(page_title="MentorMate - Success Coach AI", page_icon="🎓")

# --- UI Setup ---
st.title("Welcome to MentorMate 🎓")
st.subheader("Your AI Academic Success Coach")

# --- Sidebar / Authentication ---
with st.sidebar:
    st.header("Authentication")
    
    # Check if user is logged in
    if "logged_in_user" not in st.session_state:
        # Fetch students for dropdown
        students_dict = get_all_students()
        
        if students_dict:
            # Create options like "Rahul Verma (STU003)"
            student_options = [f"{name} ({s_id})" for s_id, name in students_dict.items()]
            selected_student = st.selectbox("Select your profile to login:", student_options)
            
            if st.button("Login"):
                st.session_state.logged_in_user = selected_student
                st.rerun()
        else:
            st.warning("Could not load student roster. Check Google Sheets connection.")
            
    else:
        st.success(f"Logged in as: {st.session_state.logged_in_user}")
        
        # --- LOGOUT & MEMORY SAVING LOGIC ---
        # Note the unique key to prevent the Streamlit duplicate ID error
        if st.button("Logout", key="save_and_logout_btn"):
            
            # 1. Check if there is an active conversation to save
            if memory_client and "messages" in st.session_state and len(st.session_state.messages) > 1:
                
                with st.spinner("Saving session notes..."):
                    # Format messages exactly how Mem0 expects them
                    mem0_messages = []
                    for msg in st.session_state.messages:
                        if isinstance(msg, HumanMessage):
                            mem0_messages.append({"role": "user", "content": msg.content})
                        elif isinstance(msg, AIMessage):
                            # Ensure we don't pass empty content to Mem0
                            if msg.content:
                                mem0_messages.append({"role": "assistant", "content": msg.content})
                    
                    # 2. Extract specific student ID from "Name (ID)" format
                    try:
                        raw_user_string = st.session_state.logged_in_user
                        if "(" in raw_user_string and ")" in raw_user_string:
                            student_id = raw_user_string.split("(")[1].split(")")[0].strip()
                        else:
                            student_id = "unknown_student"
                        
                        # Save to Mem0 cloud
                        if mem0_messages:
                            memory_client.add(mem0_messages, user_id=student_id)
                    except Exception as e:
                        st.error(f"Failed to save memory: {e}")

            # 3. Clear session and reload app
            st.session_state.clear()
            st.rerun()

# --- Main Chat Interface ---
# Only show chat if logged in
if "logged_in_user" in st.session_state:
    
    # Extract details for the prompt
    raw_user_string = st.session_state.logged_in_user
    student_first_name = raw_user_string.split(" ")[0] if raw_user_string else "Student"
    student_id_for_prompt = raw_user_string.split("(")[1].split(")")[0].strip() if "(" in raw_user_string else ""

    # Initialize chat history
    if "messages" not in st.session_state:
        # Inject the system prompt, customized with the student's name and ID
        custom_system_prompt = SYSTEM_PROMPT.format(
            student_name=student_first_name, 
            student_id=student_id_for_prompt
        )
        st.session_state.messages = [SystemMessage(content=custom_system_prompt)]
        
        # Optional: Add a welcoming first message from the AI
        st.session_state.messages.append(
            AIMessage(content=f"Hi {student_first_name}! I'm MentorMate. How can I help you today?")
        )

    # Display chat messages (excluding the hidden SystemMessage)
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage) and msg.content:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(msg.content)

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to session state
        st.session_state.messages.append(HumanMessage(content=prompt))
        
        # Get AI response
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("Thinking..."):
                agent = get_conversation_agent()
                
                # Invoke the agent with the current conversation history
                response = agent.invoke({"messages": st.session_state.messages})
                
                # The response["messages"] contains the updated history
                ai_message = response["messages"][-1]
                
                st.markdown(ai_message.content)
        
        # Save AI response to session state
        st.session_state.messages.append(ai_message)

else:
    # Message shown when not logged in
    st.info("👈 Please select your profile from the sidebar to begin your session.")