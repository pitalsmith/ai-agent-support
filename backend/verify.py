# verify.py
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- Testing API Connection ---")
try:
    # List models that support content generation
    models = client.models.list()
    print("Successfully connected to API!")
    
    print("\nAvailable models for 'generateContent' (LLM):")
    for m in models:
        if "generateContent" in m.supported_actions:
            print(f"- {m.name}")

    print("\nAvailable models for 'embedContent' (Embeddings):")
    for m in models:
        if "embedContent" in m.supported_actions:
            print(f"- {m.name}")
            
except Exception as e:
    print(f"Connection failed: {e}")