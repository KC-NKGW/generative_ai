from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class Source(BaseModel):
    source_file: str
    text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
