import streamlit as st
import requests
import pandas as pd
import os

# --- Configuration ---
# Use the environment variable provided by Render, or default to localhost
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Page Configuration
st.set_page_config(layout="wide", page_title="AI Assistant")

# --- Helper Function: Fetch from Backend ---
def get_file_list():
    try:
        # We now ask the backend for the list, not the local file system
        response = requests.get(f"{API_URL}/list-files")
        if response.status_code == 200:
            data = response.json()
            if data:
                return pd.DataFrame(data)
        return pd.DataFrame(columns=["FILE NAME", "SIZE", "ADDED"])
    except Exception as e:
        st.error(f"Could not connect to backend to fetch files: {e}")
        return pd.DataFrame(columns=["FILE NAME", "SIZE", "ADDED"])

# --- Sidebar ---
with st.sidebar:
    st.title("Mike Taylor")
    st.markdown("---")
    st.subheader("WORKSPACE")
    st.write("🏠 Home")
    st.write("👤 Team")
    st.subheader("PROJECTS")
    st.write("📂 Design System")
    st.write("📊 Marketing")
    st.markdown("---")
    st.subheader("TAGS")
    st.write("● Urgent")
    st.write("● Reviewed")

# --- Main Layout ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Upload Knowledge")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
    
    if uploaded_file is not None:
        if st.button("Index File"):
            files = {"file": (uploaded_file.name, uploaded_file)}
            try:
                response = requests.post(f"{API_URL}/upload", files=files)
                if response.status_code == 200:
                    st.success(f"Successfully indexed {uploaded_file.name}")
                    st.rerun()
                else:
                    st.error(f"Failed! Status: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
    
    st.subheader("Knowledge Base")
    df = get_file_list()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No files indexed yet.")

with col2:
    st.header("AI Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = requests.post(f"{API_URL}/ask", json={"question": prompt})
                answer = response.json().get("answer", "Error: No response from backend.")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Could not connect to the backend at {API_URL}")