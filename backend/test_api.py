# test_api.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash") # Try 1.5 instead of 3.5
print(llm.invoke("Hello, are you working?"))