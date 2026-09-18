import os

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

_model = SentenceTransformer(EMBEDDING_MODEL)


def embed(text: str) -> list[float]:
    return _model.encode(text).tolist()
