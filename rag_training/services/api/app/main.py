from fastapi import FastAPI

from app.rag import answer_question
from app.schemas import QueryRequest, QueryResponse

app = FastAPI(title="Personal RAG Assistant")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    answer, sources = answer_question(request.question, request.top_k)
    return QueryResponse(answer=answer, sources=sources)
