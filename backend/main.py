from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from query import ask_ai

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QueryRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    answer = ask_ai(request.question)
    return {"answer": answer}