import numpy as np


def sigmoid(x):
    x = float(np.clip(x, -500, 500))
    return 1.0 / (1.0 + np.exp(-x))


def confidence_signals(reranked, bm25_top5, vector_top5, temperature=1.0):
    """Return p_top, margin and retrieval agreement.

    reranked: [(chunk_id, cross_encoder_score), ...], highest score first.
    bm25_top5/vector_top5: ranked retrieval results [(chunk_id, score), ...].
    """
    if not reranked:
        return {"p_top": 0.0, "margin": 0.0, "agree": 0}

    score1 = float(reranked[0][1])
    score2 = float(reranked[1][1]) if len(reranked) > 1 else 0.0
    top_id = reranked[0][0]

    bm25_ids = {cid for cid, _ in bm25_top5[:5]}
    vector_ids = {cid for cid, _ in vector_top5[:5]}

    return {
        "p_top": sigmoid(score1 / temperature),
        "margin": score1 - score2,
        "agree": int(top_id in bm25_ids and top_id in vector_ids),
    }


def reliability(probabilities, labels, bins=5):
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(labels, dtype=float)
    edges = np.linspace(0, 1, bins + 1)
    rows = []
    ece = 0.0

    if len(p) == 0 or len(p) != len(y):
        raise ValueError("Probabilities and labels must be non-empty and equal length")

    for i in range(bins):
        mask = (p >= edges[i]) & (
            (p < edges[i + 1]) if i < bins - 1 else (p <= edges[i + 1])
        )
        if mask.sum():
            mean_p = float(p[mask].mean())
            success_rate = float(y[mask].mean())
            count = int(mask.sum())
            rows.append((edges[i], edges[i + 1], count, mean_p, success_rate))
            ece += count / len(p) * abs(mean_p - success_rate)

    return rows, float(ece)


def brier(probabilities, labels):
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(labels, dtype=float)
    if len(p) == 0 or len(p) != len(y):
        raise ValueError("Probabilities and labels must be non-empty and equal length")
    return float(np.mean((p - y) ** 2))

def mean_token_logprob(logprobs):
    """Mean token log-probability from Ollama's logprobs list."""
    values = [
        float(item["logprob"])
        for item in logprobs
        if isinstance(item, dict) and item.get("logprob") is not None
    ]
    return float(np.mean(values)) if values else None
