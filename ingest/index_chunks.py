import json
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer
from elasticsearch.helpers import bulk

from app.common import ES, sid

INDEX = "east_india_chunks_v2"
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_chunks(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def index_chunks(chunks, model_name):
    model = SentenceTransformer(model_name)
    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    actions = []

    for chunk, embedding in zip(chunks, embeddings):
        document = {
            **chunk,
            "embedding_model": model_name,
            "embedding": embedding.tolist(),
        }

        actions.append({
            "_op_type": "index",
            "_index": INDEX,
            "_id": sid(chunk["chunk_id"], model_name),
            "_source": document,
        })

    success, errors = bulk(
        ES,
        actions,
        raise_on_error=False,
        raise_on_exception=False,
    )

    print(f"Model: {model_name}")
    print(f"Chunks submitted: {len(chunks)}")
    print(f"Successfully indexed: {success}")
    print(f"Errors: {len(errors)}")

    if errors:
        print(json.dumps(errors[:3], indent=2, default=str))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python -m ingest.index_chunks <chunks.jsonl> [model_name]"
        )

    input_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL

    if not ES.indices.exists(index=INDEX):
        raise SystemExit(f"Index '{INDEX}' does not exist. Create it first.")

    chunks = load_chunks(input_path)

    if not chunks:
        raise SystemExit("No chunks found in the input file.")

    index_chunks(chunks, model_name)