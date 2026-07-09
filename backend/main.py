import os
from dotenv import load_dotenv
load_dotenv()
import shutil
import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Required for frontend/backend talk
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA

app = FastAPI()

# --- CORS Middleware ---
# Replace the URL with your final Render frontend URL once deployed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
INDEX_PATH = "faiss_index"
UPLOAD_DIR = "temp_files"
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

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
    if not os.path.exists(INDEX_PATH):
        return "Knowledge base is empty. Please upload files first."
    vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    result = qa_chain.invoke(question)
    return result["result"]

# --- Endpoints ---

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