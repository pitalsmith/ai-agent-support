import json
import os
import re
from pathlib import Path
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from app.utils import INDEX_PATH, get_google_embeddings

# Path to your JSON file
DB_FILE = "orders.json"

@tool
def get_order_status(order_id: str) -> str:
    """Check the status of a customer order from our records."""
    if not os.path.exists(DB_FILE):
        return "Database file not found."
    
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    
    order = data.get(order_id)
    if order:
        return f"Order {order_id} ({order['item']}) is currently {order['status']}."
    else:
        return f"Order {order_id} was not found."

@tool
def update_order_status(order_id: str, new_status: str) -> str:
    """Updates the status of an order in the records."""
    with open(DB_FILE, "r+") as f:
        data = json.load(f)
        if order_id in data:
            data[order_id]["status"] = new_status
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            return f"Success: Order {order_id} updated to {new_status}."
        else:
            return f"Error: Order {order_id} not found."

def handle_order_request(message: str) -> str | None:
    """Handle order status lookup/update requests from the chat UI."""
    text = message.strip().lower()
    if "order" not in text:
        return None

    order_match = re.search(r"order\s*(#?\d+)", text)
    if not order_match:
        order_match = re.search(r"\b(\d+)\b", text)
    if not order_match:
        return None

    order_id = order_match.group(1).lstrip("#")

    update_keywords = ["change", "update", "set", "modify"]
    status_keywords = ["status", "current status", "check", "what is", "what's"]

    if any(keyword in text for keyword in update_keywords) or "order status" in text:
        status_value = None
        for candidate in ["delivered", "refunded", "in progress", "processing", "shipped", "pending", "cancelled", "canceled"]:
            if candidate in text:
                status_value = candidate
                break
        if not status_value:
            to_match = re.search(r"\b(?:to|as)\s+([a-zA-Z\s]+)", text)
            if to_match:
                status_value = to_match.group(1).strip()
        if status_value:
            return update_order_status.func(order_id, status_value)

    if any(keyword in text for keyword in status_keywords) or "status" in text:
        return get_order_status.func(order_id)

    return None

@tool
def search_knowledge_base(question: str) -> str:
    """Retrieves relevant policy info from the company knowledge base."""
    from langchain_community.vectorstores import FAISS
    from app.utils import INDEX_PATH, get_google_embeddings

    if not os.path.exists(INDEX_PATH):
        return "Knowledge base is empty. Please upload documents first."

    embeddings = get_google_embeddings()
    vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = vectorstore.as_retriever().invoke(question)

    # DEBUG: Print exactly what was found to your terminal
    print(f"\n--- DEBUG RETRIEVAL ---")
    print(f"Query: {question}")
    print(f"Found {len(docs)} documents.")
    for i, doc in enumerate(docs):
        print(f"Doc {i}: {doc.page_content[:100]}...")
    print(f"-----------------------\n")

    if not docs:
        return "No relevant information found in the knowledge base."

    return "\n\n".join([doc.page_content for doc in docs])