import json
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "intfloat/e5-small-v2",
]

CHUNKS_PATH = Path("data/chunks.jsonl")
JUDGMENTS_PATH = Path("data/retrieval_judgments.jsonl")
OUTPUT_PATH = Path("data/embed_compare.json")


def load_jsonl(path):
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def recall_at_k(ranked_ids, relevant_ids, k=5):
    return (
        len(set(ranked_ids[:k]) & relevant_ids) / max(1, len(relevant_ids))
    )


def prepare_texts(model_name, texts, is_query=False):
    if model_name == "intfloat/e5-small-v2":
        prefix = "query: " if is_query else "passage: "
        return [prefix + text for text in texts]

    return texts


def evaluate_model(model_name, chunks, judgments):
    model = SentenceTransformer(model_name)

    texts = [chunk["text"] for chunk in chunks]
    passages = prepare_texts(model_name, texts)

    start = time.perf_counter()
    chunk_vectors = model.encode(
        passages,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    elapsed = time.perf_counter() - start

    chunk_vectors = np.asarray(chunk_vectors)
    chunk_ids = [chunk["chunk_id"] for chunk in chunks]

    result = {
        "model": model_name,
        "dimension": int(chunk_vectors.shape[1]),
        "max_seq_length": model.max_seq_length,
        "chunks": len(chunks),
        "encoding_seconds": round(elapsed, 4),
        "chunks_per_second": round(len(chunks) / elapsed, 2)
        if elapsed > 0 else None,
        "recall_at_5": None,
        "queries_evaluated": 0,
    }

    if not judgments:
        print(
            f"WARNING: {JUDGMENTS_PATH} not found. "
            "Recall@5 cannot be calculated."
        )
        return result

    recalls = []

    for judgment in judgments[:10]:
        query = judgment.get("query") or judgment.get("question")
        relevant_ids = (
            judgment.get("relevant_chunk_ids")
            or judgment.get("relevant_ids")
            or judgment.get("chunk_ids")
            or []
        )

        if not query or not relevant_ids:
            continue

        query_text = prepare_texts(model_name, [query], is_query=True)
        query_vector = model.encode(
            query_text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        scores = chunk_vectors @ query_vector
        top_indices = np.argsort(-scores)[:5]
        ranked_ids = [chunk_ids[i] for i in top_indices]

        recalls.append(
            recall_at_k(ranked_ids, set(relevant_ids), k=5)
        )

    if recalls:
        result["recall_at_5"] = round(float(np.mean(recalls)), 4)
        result["queries_evaluated"] = len(recalls)

    return result


def main():
    if not CHUNKS_PATH.exists():
        raise SystemExit(f"Missing chunks file: {CHUNKS_PATH}")

    chunks = load_jsonl(CHUNKS_PATH)
    if not chunks:
        raise SystemExit("No chunks found.")

    judgments = (
        load_jsonl(JUDGMENTS_PATH)
        if JUDGMENTS_PATH.exists()
        else []
    )

    results = []

    for model_name in MODELS:
        print(f"\nEvaluating {model_name}...")
        result = evaluate_model(model_name, chunks, judgments)
        results.append(result)
        print(json.dumps(result, indent=2))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()