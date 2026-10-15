def exact_match(pred, gold):
    return (pred[0], pred[1], pred[2]) == (gold[0], gold[1], gold[2])


def relaxed_match(pred, gold):
    return (
        pred[0] == gold[0]
        and min(pred[2], gold[2]) > max(pred[1], gold[1])
    )


def score_entities(predictions, gold_entities, relaxed=False):
    types = [
        "School", "Board", "Circular", "Rule",
        "Locality", "Road", "Date", "Quantity"
    ]
    results = {}

    for entity_type in types:
        preds = [e for e in predictions if e[0] == entity_type]
        golds = [e for e in gold_entities if e[0] == entity_type]
        matched_gold = set()
        tp = 0

        matcher = relaxed_match if relaxed else exact_match

        for pred in preds:
            for i, gold in enumerate(golds):
                if i not in matched_gold and matcher(pred, gold):
                    matched_gold.add(i)
                    tp += 1
                    break

        fp = len(preds) - tp
        fn = len(golds) - tp
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )

        results[entity_type] = {
            "TP": tp, "FP": fp, "FN": fn,
            "precision": precision, "recall": recall, "F1": f1
        }

    return results
