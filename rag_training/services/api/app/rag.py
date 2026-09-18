import os

from ollama import Client
from qdrant_client import QdrantClient

from app.embeddings import embed
from app.schemas import Source

QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "notes")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
ollama_client = Client(host=OLLAMA_HOST)

SYSTEM_PROMPT = (
    "あなたは提供されたメモの内容だけをもとに回答するアシスタントです。"
    "メモに書かれていないことは推測せず「わかりません」と答えてください。"
)


def search_notes(question: str, top_k: int) -> list[Source]:
    query_vector = embed(question)
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
    )
    return [
        Source(
            source_file=hit.payload["source_file"],
            text=hit.payload["text"],
            score=hit.score,
        )
        for hit in hits
    ]


def build_prompt(question: str, sources: list[Source]) -> str:
    context = "\n\n".join(f"[{s.source_file}]\n{s.text}" for s in sources)
    return (
        f"以下はユーザーのメモからの抜粋です。\n\n{context}\n\n"
        f"上記のメモを参考に、次の質問に日本語で答えてください。\n質問: {question}"
    )


def answer_question(question: str, top_k: int = 5) -> tuple[str, list[Source]]:
    sources = search_notes(question, top_k)

    if not sources:
        return "関連するメモが見つかりませんでした。", []

    prompt = build_prompt(question, sources)
    response = ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    answer = response["message"]["content"]
    return answer, sources
