"""notesディレクトリを読み込み、チャンク分割してQdrantに登録するバッチジョブ。"""
import os
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

NOTES_DIR = Path(os.environ.get("NOTES_DIR", "/data/notes"))
QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "notes")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]


def load_notes() -> list[tuple[str, str]]:
    files = sorted(NOTES_DIR.glob("*.md"))
    return [(f.name, f.read_text(encoding="utf-8")) for f in files]


def main() -> None:
    notes = load_notes()
    if not notes:
        raise SystemExit(f"No notes found in {NOTES_DIR}")

    print(f"Loaded {len(notes)} note files from {NOTES_DIR}")

    model = SentenceTransformer(EMBEDDING_MODEL)
    vector_size = model.get_sentence_embedding_dimension()

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    points = []
    for filename, content in notes:
        for chunk in chunk_text(content):
            embedding = model.encode(chunk).tolist()
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={"text": chunk, "source_file": filename},
                )
            )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Upserted {len(points)} chunks into collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    main()
