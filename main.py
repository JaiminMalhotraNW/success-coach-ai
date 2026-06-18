import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agents.conversation_agent import get_conversation_agent

st.set_page_config(page_title="Success Coach AI", page_icon="🎓")

if "current_student" not in st.session_state: st.session_state.current_student = None

if st.session_state.current_student is None:
    st.title("🎓 Success Coach AI Login")
    roster = {"STU001": "Arjun Kumar", "STU002": "Priya Sharma", "STU003": "Rahul Verma"}
    selected_id = st.selectbox("Select Profile", options=list(roster.keys()), format_func=lambda x: f"{x} - {roster[x]}")
    if st.button("Log In"):
        st.session_state.current_student = {"id": selected_id, "name": roster[selected_id]}
        st.session_state.messages = [{"role": "assistant", "content": f"Hi {roster[selected_id]}! How can I help?"}]
        st.rerun()
else:
    student_name, student_id = st.session_state.current_student["name"], st.session_state.current_student["id"]
    st.title(f"🧑‍🎓 {student_name}'s Portal")
    if st.button("Log Out"): st.session_state.current_student = None; st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # System message ensures the agent always knows the ID context
        lc_messages = [SystemMessage(content=f"You are a coach for {student_name} (ID: {student_id}). Always use this ID for tool queries.")]
        for msg in st.session_state.messages:
            lc_messages.append(HumanMessage(content=msg["content"]) if msg["role"]=="user" else AIMessage(content=msg["content"]))

        with st.chat_message("assistant"):
            agent = get_conversation_agent()
            response = agent.invoke({"messages": lc_messages})["messages"][-1].content
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})