"""Évalue le modèle sauvegardé sur le test set et vérifie les critères du TP."""
import json
import time

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from src.utils.config import (
    FIGURES_DIR,
    LABEL_NAMES,
    LABELS,
    MODEL_PATH,
    REPORTS_DIR,
    TEST_PATH,
    VECTORIZER_PATH,
)

MIN_ACCURACY = 0.80
MIN_F1 = 0.75
MAX_BATCH_MS = 100
BATCH_SIZE = 50


def batch_latency_ms(vectorizer, model, texts, repeats: int = 100) -> dict:
    timings = []
    for i in range(repeats):
        batch = texts.sample(BATCH_SIZE, random_state=i).tolist()
        start = time.perf_counter()
        model.predict_proba(vectorizer.transform(batch))
        timings.append((time.perf_counter() - start) * 1000)
    return {"mean": round(float(np.mean(timings)), 2), "p95": round(float(np.percentile(timings, 95)), 2)}


def main() -> None:
    test = pd.read_csv(TEST_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(MODEL_PATH)

    y_pred = model.predict(vectorizer.transform(test["text"]))
    accuracy = float(accuracy_score(test["label"], y_pred))
    names = [LABEL_NAMES[i] for i in LABELS]
    report = classification_report(
        test["label"], y_pred, labels=LABELS, target_names=names, output_dict=True
    )
    latency = batch_latency_ms(vectorizer, model, test["text"])

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    matrix = confusion_matrix(test["label"], y_pred, labels=LABELS)
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(matrix, display_labels=names).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Matrice de confusion (test set)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    f1_by_class = {n: round(report[n]["f1-score"], 4) for n in names}
    results = {
        "n_test": int(len(test)),
        "accuracy": round(accuracy, 4),
        "f1_by_class": f1_by_class,
        "precision_by_class": {n: round(report[n]["precision"], 4) for n in names},
        "recall_by_class": {n: round(report[n]["recall"], 4) for n in names},
        "f1_macro": round(report["macro avg"]["f1-score"], 4),
        "confusion_matrix": matrix.tolist(),
        "batch50_latency_ms": latency,
        "criteria": {
            "accuracy_ge_80": accuracy >= MIN_ACCURACY,
            "f1_each_class_gt_75": all(v > MIN_F1 for v in f1_by_class.values()),
            "batch50_lt_100ms": latency["p95"] < MAX_BATCH_MS,
        },
    }
    (REPORTS_DIR / "metrics.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
