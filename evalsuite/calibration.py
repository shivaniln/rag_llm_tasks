import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss

from retrieve.confidence import reliability, brier


def load_questions(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing required dataset: {path}")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError(f"Dataset is empty: {path}")
    return rows


def fit_confidence_model(fit_rows):
    """Rows require features [p_top, margin, agree, lp] and binary label y."""
    X = np.asarray([r["features"] for r in fit_rows], dtype=float)
    y = np.asarray([r["y"] for r in fit_rows], dtype=int)
    if len(y) != 25:
        raise ValueError(f"Expected 25 fit questions, got {len(y)}")
    if len(set(y)) < 2:
        raise ValueError("Fit labels must contain both success and failure")
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=0.5, max_iter=1000, random_state=42),
    )
    model.fit(X, y)
    return model


def evaluate_test(model, test_rows):
    """Test rows require features and y; does not tune on test labels."""
    X = np.asarray([r["features"] for r in test_rows], dtype=float)
    y = np.asarray([r["y"] for r in test_rows], dtype=int)
    if len(y) != 15:
        raise ValueError(f"Expected 15 test questions, got {len(y)}")
    p = model.predict_proba(X)[:, 1]
    bins, ece = reliability(p, y, bins=5)
    return {
        "count": len(y),
        "mean_confidence": float(p.mean()),
        "success_rate": float(y.mean()),
        "calibration": "over-confident" if p.mean() > y.mean() else "under-confident",
        "ece": ece,
        "brier": brier(p, y),
        "reliability_bins": bins,
    }


def temperature_scaling(scores, labels):
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=int)
    if len(scores) != 25:
        raise ValueError(f"Expected 25 fit scores, got {len(scores)}")
    candidates = np.arange(0.5, 3.01, 0.25)
    results = []
    for t in candidates:
        p = 1 / (1 + np.exp(-np.clip(scores / t, -500, 500)))
        results.append((float(t), float(log_loss(labels, p, labels=[0, 1]))))
    return min(results, key=lambda row: row[1]), results


def abstention_table(probabilities, labels, thresholds=(0.3, 0.4, 0.5, 0.6, 0.7)):
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(labels, dtype=int)
    rows = []
    for threshold in thresholds:
        answered = p >= threshold
        count = int(answered.sum())
        rows.append({
            "threshold": float(threshold),
            "coverage": float(count / len(y)) if len(y) else 0.0,
            "accuracy": float(y[answered].mean()) if count else None,
            "answered": count,
            "total": len(y),
        })
    eligible = [r for r in rows if r["accuracy"] is not None and r["accuracy"] >= 0.90]
    chosen = min(eligible, key=lambda r: r["threshold"]) if eligible else max(
        rows, key=lambda r: (-1 if r["accuracy"] is None else r["accuracy"], r["coverage"])
    )
    return rows, chosen


if __name__ == "__main__":
    for name in ("data/calibration_questions.jsonl", "data/dev_questions.jsonl"):
        try:
            rows = load_questions(name)
            print(name, "questions:", len(rows))
        except (FileNotFoundError, ValueError) as exc:
            print("BLOCKED:", exc)
