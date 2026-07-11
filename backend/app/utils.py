import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_groq import ChatGroq
# Use this classic import for the RAG chain
from langchain_classic.chains import RetrievalQA

# Load environment from the repository root .env file
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

INDEX_PATH = "faiss_index"

def get_google_api_key():
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


def get_google_embeddings(model="gemini-embedding-2"):
    api_key = get_google_api_key()
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY or GEMINI_API_KEY must be set for Gemini embeddings."
        )
    return GoogleGenerativeAIEmbeddings(model=model, google_api_key=api_key)


embeddings = get_google_embeddings()

def ask_ai(question):
    
    # Load the vectorstore
    vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    llm = ChatGroq(model="llama-3.1-8b-instant")
    
    # Use RetrievalQA instead of the newer create_retrieval_chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=vectorstore.as_retriever()
    )
    
    result = qa_chain.invoke({"query": question})
    return result["result"]