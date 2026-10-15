import json
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer
from elasticsearch.helpers import bulk

from app.common import ES

INDEX = "east_india_chunks_v3"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_chunks(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def index_chunks(chunks):
    model = SentenceTransformer(MODEL_NAME)

    texts = [chunk["text"] for chunk in chunks]

    vectors = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    def actions():
        for chunk, vector in zip(chunks, vectors):
            yield {
                "_op_type": "index",
                "_index": INDEX,
                "_id": chunk["chunk_id"],
                "_source": {
                    **chunk,
                    "embedding_model": MODEL_NAME,
                    "embedding": vector.tolist(),
                },
            }

    success, errors = bulk(
        ES,
        actions(),
        chunk_size=200,
        raise_on_error=False,
        raise_on_exception=False,
    )

    ES.indices.refresh(index=INDEX)

    count = ES.count(index=INDEX)["count"]

    print(f"Chunks submitted: {len(chunks)}")
    print(f"Successfully indexed: {success}")
    print(f"Errors: {len(errors)}")
    print(f"Documents in index: {count}")

    if errors:
        print(json.dumps(errors[:3], indent=2, default=str))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m ingest.index_chunks_v3 data/chunks.jsonl"
        )

    chunks = load_chunks(sys.argv[1])

    if not chunks:
        raise SystemExit("No chunks found in the input file.")

    index_chunks(chunks)