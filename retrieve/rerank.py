from sentence_transformers import CrossEncoder
import time

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_model = None


def get_model():
    global _model
    if _model is None:
        _model = CrossEncoder(MODEL_NAME, max_length=512)
    return _model


def rerank(query, candidates, texts, batch_size=16):
    """Candidates: [(chunk_id, retrieval_score), ...].
    Texts: {chunk_id: passage_text}.
    Returns [(chunk_id, cross_encoder_score), ...].
    """
    if not candidates:
        return []

    model = get_model()
    pairs = [(query, texts[cid]) for cid, _ in candidates if cid in texts]
    ids = [cid for cid, _ in candidates if cid in texts]

    scores = model.predict(pairs, batch_size=batch_size, show_progress_bar=False)
    return sorted(
        zip(ids, scores.tolist()),
        key=lambda item: (-item[1], item[0]),
    )


def rerank_timed(query, candidates, texts, batch_size=16):
    start = time.perf_counter()
    results = rerank(query, candidates, texts, batch_size)
    return results, time.perf_counter() - start
