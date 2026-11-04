import time

import joblib
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, f1_score

from src.api.predictor import SentimentPredictor
from src.utils.config import LABELS, MODEL_PATH, TEST_PATH, VECTORIZER_PATH


@pytest.fixture(scope="module")
def predictor():
    return SentimentPredictor()


@pytest.mark.skipif(not TEST_PATH.exists(), reason="Lancer src.data.prepare d'abord")
def test_performance_criteria():
    test = pd.read_csv(TEST_PATH)
    model, vectorizer = joblib.load(MODEL_PATH), joblib.load(VECTORIZER_PATH)
    predicted = model.predict(vectorizer.transform(test["text"]))
    assert accuracy_score(test["label"], predicted) >= 0.80
    assert min(f1_score(test["label"], predicted, labels=LABELS, average=None)) > 0.75


def test_batch_of_50_under_100ms(predictor):
    comments = ["this video is really great and helpful"] * 50
    predictor.predict(comments)  # Le premier appel n'est pas représentatif.
    start = time.perf_counter()
    predictor.predict(comments)
    assert (time.perf_counter() - start) * 1000 < 100


@pytest.mark.parametrize("text, label", [
    ("This video is amazing, thank you so much!", 1),
    ("I love this song so much ❤️", 1),
    ("This is the worst video I have ever seen", -1),
    ("I hate this channel", -1),
    ("What camera do you use?", 0),
])
def test_obvious_comments(predictor, text, label):
    assert predictor.predict([text])[0]["label"] == label


@pytest.mark.parametrize("text", [
    "a",
    "ok " * 5000,
    "😀😀😀",
    "C'est génial, really love it, شكرا",
    "1234 !!! ???",
])
def test_edge_cases_return_valid_output(predictor, text):
    result = predictor.predict([text])[0]
    assert result["label"] in LABELS
    assert 0 <= result["confidence"] <= 1


@pytest.mark.parametrize("text", ["", "🦄", "شكرا جزيلا", "!!!"])
def test_unanalyzable_text_is_neutral_without_confidence(predictor, text):
    result = predictor.predict([text])[0]
    assert (result["label"], result["confidence"]) == (0, 0.0)


@pytest.mark.xfail(reason="Limite connue du modèle unigramme : il ne gère pas la négation")
def test_negation(predictor):
    assert predictor.predict(["This is not good at all"])[0]["label"] == -1
