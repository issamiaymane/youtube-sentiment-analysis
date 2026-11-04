"""Analyse exploratoire : distribution des classes et longueur des textes."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.utils.config import CLEAN_PATH, FIGURES_DIR, LABEL_NAMES, LABELS, REPORTS_DIR

COLORS = {-1: "#c0392b", 0: "#7f8c8d", 1: "#27ae60"}


def main() -> None:
    df = pd.read_csv(CLEAN_PATH)
    df["n_words"] = df["text"].str.split().str.len()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    counts = df["label"].value_counts().reindex(LABELS)
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar([LABEL_NAMES[i] for i in LABELS], counts, color=[COLORS[i] for i in LABELS])
    ax.bar_label(bars)
    ax.set_title("Distribution des classes")
    ax.set_ylabel("Commentaires")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "class_distribution.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    for label in LABELS:
        subset = df.loc[df["label"] == label, "n_words"].clip(upper=100)
        ax.hist(subset, bins=50, alpha=0.5, label=LABEL_NAMES[label], color=COLORS[label])
    ax.set_title("Longueur des commentaires (coupée à 100 mots)")
    ax.set_xlabel("Mots")
    ax.set_ylabel("Commentaires")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "text_length.png", dpi=150)
    plt.close(fig)

    stats = {
        "n_comments": int(len(df)),
        "class_counts": {LABEL_NAMES[i]: int(counts[i]) for i in LABELS},
        "class_ratio_max_min": round(float(counts.max() / counts.min()), 2),
        "median_words_by_class": {
            LABEL_NAMES[i]: float(df.loc[df["label"] == i, "n_words"].median()) for i in LABELS
        },
        "words_describe": df["n_words"].describe().round(1).to_dict(),
    }
    (REPORTS_DIR / "eda.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False))
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
