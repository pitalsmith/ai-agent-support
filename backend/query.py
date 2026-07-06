import os
from dotenv import load_dotenv
# Keep Google embeddings so your existing FAISS index still works
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# Import Groq
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# 1. Embeddings remain Google (to match your ./faiss_index)
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001", # You can also try "gemini-embedding-2"
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
# 2. Switch LLM to Groq
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Loading local FAISS index
vectorstore = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever()

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

@retry(
    stop=stop_after_attempt(5), 
    wait=wait_exponential(multiplier=2, min=5, max=60)
)
def ask_ai(question: str):
    try:
        return rag_chain.invoke(question)
    except Exception as e:
        return f"Error: {str(e)}"