from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import query_fifa

app = FastAPI(title="FIFA AI Analyst API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class QuestionRequest(BaseModel):
    question: str
    n_results: int = 5

class AnswerResponse(BaseModel):
    answer: str
    sources: list

@app.get("/health")
def health():
    return {"status": "ok", "message": "FIFA AI Analyst is running"}

@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    result = query_fifa(request.question, request.n_results)
    return AnswerResponse(answer=result["answer"], sources=result["sources"])