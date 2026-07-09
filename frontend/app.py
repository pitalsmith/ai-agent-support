import streamlit as st
import requests
import pandas as pd
import os

# --- Configuration ---
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Page Configuration
st.set_page_config(layout="wide", page_title="AI Assistant")

# --- Helper Function: Fetch from Backend ---
def get_file_list():
    try:
        response = requests.get(f"{API_URL}/list-files")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame(columns=["FILE NAME", "SIZE", "ADDED"])
    except Exception as e:
        st.error(f"Backend connection error: {e}")
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
    
    # Knowledge Base in Sidebar (Scrollable)
    st.subheader("Knowledge Base")
    df = get_file_list()
    
    # Native Streamlit Scrollable Container
    with st.container(height=300, border=True):
        if not df.empty:
            for index, row in df.iterrows():
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(f"📄 {row['FILE NAME']}")
                with col2:
                    if st.button("🗑️", key=f"del_{row['FILE NAME']}"):
                        requests.delete(f"{API_URL}/delete-file/{row['FILE NAME']}")
                        st.rerun()
        else:
            st.info("No files indexed.")

# --- Main Layout ---
st.header("AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
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
            st.error(f"Connection Error: {e}")

# Upload Section (Main Area)
with st.expander("Upload New Knowledge"):
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
    if uploaded_file and st.button("Index File"):
        files = {"file": (uploaded_file.name, uploaded_file)}
        try:
            response = requests.post(f"{API_URL}/upload", files=files)
            if response.status_code == 200:
                st.success(f"Indexed {uploaded_file.name}")
                st.rerun()
        except Exception as e:
            st.error(f"Upload failed: {e}")