import sys
import os

# PATH FIX: Force Python to recognize your project folders
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import streamlit as st
from config.llm import get_llm
from langchain_core.messages import HumanMessage, AIMessage

# Setup the page layout
st.set_page_config(page_title="Success Coach AI", page_icon="🎓")
st.title("🧑‍🎓 Success Coach AI - Student Portal")

# Initialize the chat history in Streamlit's session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I am your Success Coach AI. How can I help you today?"}
    ]

# Display all existing chat messages on screen re-run
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask me anything..."):
    # Display the student's message instantly
    st.chat_message("user").markdown(prompt)
    
    # Save student's message to local session history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Convert session history into LangChain message formats
    lc_messages = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))

    # Request a completion from OpenAI and display the streaming response
    with st.chat_message("assistant"):
        llm = get_llm()
        response = llm.invoke(lc_messages)
        st.markdown(response.content)
        
    # Save the AI's response back to history
    st.session_state.messages.append({"role": "assistant", "content": response.content})