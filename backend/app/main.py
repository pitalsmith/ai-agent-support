import json
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
import shutil
import datetime
from fastapi import FastAPI,Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Required for frontend/backend talk
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA
from app.agents.support_agent import graph
from fastapi import FastAPI, UploadFile, File
from app.utils import ask_ai, get_google_embeddings

import re
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


def extract_title_from_answer(answer: str) -> str | None:
    if not answer:
        return None

    lines = [line.strip() for line in str(answer).splitlines() if line.strip()]
    if not lines:
        return None

    first_line = lines[0]
    if first_line.lower().startswith(("financial fraud management policy", "policy")):
        return first_line

    cleaned = re.sub(r"\s+", " ", str(answer)).strip()
    title_match = re.search(r"([A-Z][A-Z0-9\s&/()-]{3,})", cleaned)
    if title_match:
        title = title_match.group(1).strip()
        if title.lower().endswith(("policy", "policies")) or "policy" in title.lower():
            return title

    return None


app = FastAPI(title="AI Agent Support API")

class ChatRequest(BaseModel):
    message: str

# --- CORS Middleware ---
# Allow frontend access during Render deployment.
# For greater security, replace ['*'] with your deployed frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
INDEX_PATH = "faiss_index"
UPLOAD_DIR = "temp_files"
ORDERS_FILE = Path(__file__).resolve().parents[1] / "orders.json"


def get_embeddings():
    try:
        return get_google_embeddings(model="gemini-embedding-2-preview")
    except EnvironmentError:
        return None

class QueryRequest(BaseModel):
    question: str

# --- Helper: Indexing & Query Logic (Kept as you had it) ---
def process_and_index_file(file_path):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    if os.path.exists(INDEX_PATH):
        vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(splits)
    else:
        vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(INDEX_PATH)

def ask_ai(question: str):
    embeddings = get_embeddings()
    if not embeddings:
        return "GOOGLE_API_KEY or GEMINI_API_KEY must be set for Gemini embeddings."
    if not os.path.exists(INDEX_PATH):
        return "Knowledge base is empty. Please upload files first."
    vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    result = qa_chain.invoke(question)
    return result["result"]

# --- Endpoints ---
@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        # 1. Safely get the request data
        data = await request.json()
        user_message = data.get("user_query")
        
        if not user_message:
            return JSONResponse(status_code=400, content={"response": "Error: No message content provided."})

        print(f"DEBUG: Processing message: {user_message}")

        from app.tools.order_tool import handle_order_request
        order_response = handle_order_request(user_message)
        if order_response:
            return {"response": order_response}

        lower_message = user_message.lower()
        if "order status" in lower_message and ("update" in lower_message or "change" in lower_message or "set" in lower_message):
            from app.tools.order_tool import update_order_status
            order_match = re.search(r"order\s*(#?\d+)", lower_message)
            if order_match:
                order_id = order_match.group(1).lstrip("#")
                status_match = re.search(r"(?:to|as)\s+([a-zA-Z\s]+)$", lower_message)
                if status_match:
                    return {"response": update_order_status.func(order_id, status_match.group(1).strip())}

        if any(keyword in lower_message for keyword in ["policy name", "policy title", "what is my policy", "what is the title"]):
            try:
                from app.tools.order_tool import search_knowledge_base
                retrieved_content = search_knowledge_base.invoke(user_message)
                title = extract_title_from_answer(retrieved_content)
                if title:
                    return {"response": title}

                direct_answer = ask_ai(user_message)
                if direct_answer and "Knowledge base is empty" not in direct_answer:
                    return {"response": direct_answer}
            except Exception as e:
                print(f"DEBUG: policy-name fallback failed: {e}")

        try:
            direct_answer = ask_ai(user_message)
            if direct_answer and "Knowledge base is empty" not in direct_answer:
                return {"response": direct_answer}
        except Exception as e:
            print(f"DEBUG: direct knowledge-base fallback failed: {e}")

        print("DEBUG: Invoking graph...")

        # 2. Invoke the graph with a timeout/recursion limit to prevent hangs
        # We pass the message in the format your LangGraph expects
        initial_state = {"messages": [("user", user_message)]}
        result = graph.invoke(initial_state, config={"recursion_limit": 25})
        
        print("DEBUG: Graph invocation complete!")

        # 3. Extract the final response
        if "messages" in result and result["messages"]:
            final_content = result["messages"][-1].content
            
            # 4. Clean up any lingering tool-calling tags (like <brave_search>)
            clean_answer = re.sub(r'<[^>]+>', '', final_content).strip()
            
            return {"response": clean_answer}
        else:
            return {"response": "The agent did not return a valid response."}

    except Exception as e:
        # 5. Log the error to your terminal so you can fix it
        print(f"CRITICAL ERROR in /chat: {str(e)}")
        # Return the error to the frontend so you can see it in the UI
        return {"response": f"Backend Error: {str(e)}"}


@app.get("/orders")
async def get_orders():
    if not ORDERS_FILE.exists():
        return {}
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

@app.get("/list-files")
async def list_files():
    """Returns the list of uploaded files for the frontend to display."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    files_data = []
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(filepath):
            size_kb = round(os.path.getsize(filepath) / 1024, 2)
            mtime = os.path.getmtime(filepath)
            date_added = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            files_data.append({
                "FILE NAME": filename,
                "SIZE": f"{size_kb} KB",
                "ADDED": date_added
            })
    return files_data

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        process_and_index_file(file_location)
        return {"message": f"File {file.filename} indexed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QueryRequest):
    answer = ask_ai(request.question)
    return {"answer": answer}

@app.delete("/delete-file/{filename}")
async def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
        # After deleting, you should ideally rebuild the index 
        # or clear it. For simplicity, we'll just delete the FAISS index
        # so the user can start fresh.
        if os.path.exists(INDEX_PATH):
            shutil.rmtree(INDEX_PATH)
            
        return {"message": f"Deleted {filename} and cleared index."}
    else:
        raise HTTPException(status_code=404, detail="File not found")