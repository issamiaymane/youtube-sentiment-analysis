"""Chargement du modèle et prédiction par batch."""
import joblib
import numpy as np

from src.data.preprocessing import clean_text
from src.utils.config import LABEL_NAMES, LABELS, MODEL_PATH, VECTORIZER_PATH


class SentimentPredictor:
    def __init__(self, model_path=MODEL_PATH, vectorizer_path=VECTORIZER_PATH):
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)

    def predict(self, comments: list[str]) -> list[dict]:
        cleaned = [clean_text(comment) for comment in comments]
        probabilities = self.model.predict_proba(self.vectorizer.transform(cleaned))
        indices = probabilities.argmax(axis=1)
        labels = self.model.classes_[indices]
        confidences = probabilities[np.arange(len(comments)), indices]

        predictions = []
        for text, clean, label, confidence in zip(comments, cleaned, labels, confidences):
            # Rien d'analysable (emoji inconnu, autre alphabet) : neutre, sans aucune confiance.
            label, confidence = (int(label), float(confidence)) if clean else (0, 0.0)
            predictions.append({
                "text": text,
                "label": label,
                "sentiment": LABEL_NAMES[label],
                "confidence": round(confidence, 4),
            })
        return predictions


def compute_statistics(predictions: list[dict]) -> dict:
    total = len(predictions)
    counts = {LABEL_NAMES[label]: 0 for label in LABELS}
    for prediction in predictions:
        counts[prediction["sentiment"]] += 1
    return {
        "total": total,
        "counts": counts,
        "percentages": {name: round(100 * n / total, 1) for name, n in counts.items()},
        "average_confidence": round(sum(p["confidence"] for p in predictions) / total, 4),
    }
