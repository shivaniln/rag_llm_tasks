import json
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "intfloat/e5-small-v2",
]

TEXTS = [
    "Schools in a district provide primary education.",
    "Roads connect schools and nearby localities.",
    "Admission rules are published in official circulars.",
    "A locality may contain multiple educational institutions.",
    "District guidelines specify eligibility and required documents.",
] * 20


def benchmark(model_name):
    model = SentenceTransformer(model_name)

    # Warm-up to reduce first-call loading effects.
    model.encode(TEXTS[:2], normalize_embeddings=True)

    start = time.perf_counter()
    embeddings = model.encode(
        TEXTS,
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    elapsed = time.perf_counter() - start

    embeddings = np.asarray(embeddings)

    return {
        "model": model_name,
        "documents": len(TEXTS),
        "dimensions": int(embeddings.shape[1]),
        "elapsed_seconds": round(elapsed, 4),
        "documents_per_second": round(len(TEXTS) / elapsed, 2),
        "finite_values": bool(np.isfinite(embeddings).all()),
        "normalized": bool(
            np.allclose(np.linalg.norm(embeddings, axis=1), 1.0, atol=1e-4)
        ),
    }


if __name__ == "__main__":
    results = []

    for model_name in MODELS:
        print(f"Benchmarking {model_name}...")
        result = benchmark(model_name)
        results.append(result)
        print(json.dumps(result, indent=2))

    output = Path("data/embedding_benchmark.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"\nSaved benchmark results to {output}")