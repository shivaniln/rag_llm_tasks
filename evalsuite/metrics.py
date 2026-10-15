import math


def precision_at_k(ranked, rel, k):
    if k <= 0:
        return 0.0
    return sum(1 for c in ranked[:k] if rel.get(c, 0) > 0) / k


def recall_at_k(ranked, rel, k):
    total = sum(1 for grade in rel.values() if grade > 0)
    if total == 0:
        return 0.0
    return sum(1 for c in ranked[:k] if rel.get(c, 0) > 0) / total


def mrr(ranked, rel):
    for i, chunk_id in enumerate(ranked, 1):
        if rel.get(chunk_id, 0) > 0:
            return 1 / i
    return 0.0


def dcg(gains):
    return sum(
        (2**grade - 1) / math.log2(i + 2)
        for i, grade in enumerate(gains)
    )


def ndcg_at_k(ranked, rel, k):
    ideal = dcg(sorted(rel.values(), reverse=True)[:k])
    if ideal == 0:
        return 0.0
    return dcg([rel.get(c, 0) for c in ranked[:k]]) / ideal