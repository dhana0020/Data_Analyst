
import streamlit as st


def initialize_chat():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def add_message(role, content):
    st.session_state.chat_history.append({
        "role": role,
        "content": str(content)
    })


def get_chat_history():
    return st.session_state.chat_history


def clear_chat():
    st.session_state.chat_history = []


def display_chat_history():
    initialize_chat()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
