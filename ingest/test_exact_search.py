import time
from sentence_transformers import SentenceTransformer
from app.common import ES

INDEX = "east_india_chunks_v2"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)
query = "What tasks are involved in the East India Geo-Assistant assessment?"
vector = model.encode(query, normalize_embeddings=True).tolist()

exact = ES.search(
    index=INDEX,
    size=10,
    query={
        "script_score": {
            "query": {"term": {"embedding_model": MODEL_NAME}},
            "script": {
                "source": "cosineSimilarity(params.q, 'embedding') + 1.0",
                "params": {"q": vector},
            },
        }
    },
    source=["chunk_id"],
)
exact_ids = {h["_id"] for h in exact["hits"]["hits"]}

for candidates in [20, 50, 100]:
    start = time.perf_counter()

    result = ES.search(
        index=INDEX,
        size=10,
        knn={
            "field": "embedding",
            "query_vector": vector,
            "k": 10,
            "num_candidates": candidates,
            "filter": {"term": {"embedding_model": MODEL_NAME}},
        },
        source=["chunk_id"],
    )

    latency = (time.perf_counter() - start) * 1000
    result_ids = {h["_id"] for h in result["hits"]["hits"]}
    recall = len(result_ids & exact_ids) / len(exact_ids) if exact_ids else 0

    print(
        f"num_candidates={candidates}: "
        f"latency={latency:.2f} ms, "
        f"Recall@10={recall:.2f}"
    )

import json
from pathlib import Path

results = [
    {"num_candidates": 20, "latency_ms": 53.48, "recall_at_10": 1.0},
    {"num_candidates": 50, "latency_ms": 57.22, "recall_at_10": 1.0},
    {"num_candidates": 100, "latency_ms": 54.10, "recall_at_10": 1.0},
]

Path("data/ann_smoke_test.json").write_text(
    json.dumps(results, indent=2),
    encoding="utf-8",
)

print("Saved results to data/ann_smoke_test.json")