from sentence_transformers import SentenceTransformer

from app.common import ES

INDEX = "east_india_chunks_v3"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def embed_query(q):
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model.encode(q, normalize_embeddings=True)


def bm25(q, k=20, flt=None):
    query = {
        "bool": {
            "must": [{"match": {"text": q}}],
            "filter": flt or [],
        }
    }

    r = ES.search(
        index=INDEX,
        query=query,
        size=k,
        source=["chunk_id", "doc", "page", "text"],
    )

    return [(h["_id"], h["_score"]) for h in r["hits"]["hits"]]


def vector(q, k=20, nc=100, flt=None):
    qv = embed_query(q)

    r = ES.search(
        index=INDEX,
        size=k,
        knn={
            "field": "embedding",
            "query_vector": qv.tolist(),
            "k": k,
            "num_candidates": nc,
            **({"filter": flt} if flt else {}),
        },
        source=["chunk_id", "doc", "page", "text"],
    )

    return [(h["_id"], h["_score"]) for h in r["hits"]["hits"]]


def rrf(lists, k=60, top=20):
    scores = {}

    for result_list in lists:
        for rank, (chunk_id, _) in enumerate(result_list, 1):
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank)

    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:top]


def hybrid(q, k=20, rrf_k=60, flt=None):
    return rrf(
        [bm25(q, 50, flt), vector(q, 50, 100, flt)],
        k=rrf_k,
        top=k,
    )


def graph_hybrid(q, k=20, flt=None):
    # Task 4 entity detection and graph expansion are not implemented yet.
    # Return hybrid results until expand() and detect_entities() are available.
    return hybrid(q, k=k, flt=flt)