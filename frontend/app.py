import streamlit as st
import requests
import os

import faulthandler
faulthandler.enable()

# --- Configuration ---
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Page Configuration
st.set_page_config(layout="wide", page_title="AI Assistant")


# --- Helper Function: Fetch from Backend ---
def get_file_list():
    try:
        response = requests.get(f"{API_URL}/list-files")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return []


def send_chat_message(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        try:
            response = requests.post(f"{API_URL}/chat", json={"user_query": prompt})
            if response.status_code == 200:
                answer = response.json().get("response", "Empty response.")
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                answer = f"Error: {response.status_code}"
                message_placeholder.error(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            answer = f"Connection Error: {e}"
            message_placeholder.error(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

    return answer


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

    st.subheader("Order Database")
    with st.container(height=220, border=True):
        try:
            orders_response = requests.get(f"{API_URL}/orders")
            if orders_response.status_code == 200:
                orders = orders_response.json()
                st.write(f"Total orders: {len(orders)}")
                for order_id, details in list(orders.items())[:10]:
                    st.write(f"• {order_id}: {details.get('item', 'Unknown')} — {details.get('status', 'unknown')}")
            else:
                st.info("Order database unavailable")
        except Exception as e:
            st.info(f"Could not load orders: {e}")

    st.markdown("---")

    # Knowledge Base
    st.subheader("Knowledge Base")
    files = get_file_list()

    if files:
        st.metric("Files indexed", len(files))
        st.caption(f"Latest: {files[-1]['FILE NAME']}")
    else:
        st.metric("Files indexed", 0)
        st.info("No files indexed.")

    with st.container(height=300, border=True):
        if files:
            header_col1, header_col2 = st.columns([0.78, 0.22])
            with header_col1:
                st.markdown("**File**")
            with header_col2:
                st.markdown("**Action**")

            for row in files:
                file_name = row["FILE NAME"]
                display_name = file_name if len(file_name) <= 28 else f"{file_name[:25]}..."
                row_col1, row_col2 = st.columns([0.78, 0.22])
                with row_col1:
                    st.write(f"📄 {display_name}")
                with row_col2:
                    if st.button("🗑️", key=f"del_{file_name}"):
                        requests.delete(f"{API_URL}/delete-file/{file_name}")
                        st.rerun()
        else:
            st.info("No files indexed.")

# --- Main Layout ---
st.header("AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Check for new input
if prompt := st.chat_input("Ask a question..."):
    send_chat_message(prompt)
    st.rerun()

# Upload Section
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