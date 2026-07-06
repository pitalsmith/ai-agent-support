import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def ingest_document(file_path):
    # 1. Load the PDF
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # 2. Split the document into chunks
    # Using RecursiveCharacterTextSplitter is recommended for better context retention
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    
    # 3. Embed and create vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # 4. Save to disk
    vectorstore.save_local("faiss_index")
    print(f"Successfully ingested {file_path} and saved index to 'faiss_index'")

if __name__ == "__main__":
    # Ensure this path matches the location of your actual file
    ingest_document("data/policy.pdf")