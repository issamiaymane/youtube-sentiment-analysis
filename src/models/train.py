"""Compare plusieurs algorithmes, optimise la régression logistique et sauvegarde le modèle.

Toute la sélection se fait en validation croisée sur le train. Le test set n'est utilisé
qu'une seule fois, par src/models/evaluate.py.
"""
import json

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import make_scorer, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from src.utils.config import (
    MODEL_PATH,
    MODELS_DIR,
    RANDOM_STATE,
    REPORTS_DIR,
    TRAIN_PATH,
    VECTORIZER_PATH,
)
from src.utils.logger import get_logger

logger = get_logger("train")
CV = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
SCORING = {"accuracy": "accuracy", "f1_macro": make_scorer(f1_score, average="macro")}


def base_vectorizer() -> TfidfVectorizer:
    # Pas de stop words : la liste anglaise retirerait "not", "no"... qui inversent le sentiment.
    return TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000, sublinear_tf=True)


def compare_algorithms(X, y) -> dict:
    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "linear_svm": LinearSVC(class_weight="balanced"),
        "naive_bayes": MultinomialNB(),
        "random_forest": RandomForestClassifier(
            n_estimators=100, max_depth=40, class_weight="balanced", n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }
    results = {}
    for name, clf in candidates.items():
        pipe = Pipeline([("tfidf", base_vectorizer()), ("clf", clf)])
        scores = cross_validate(pipe, X, y, cv=CV, scoring=SCORING)
        results[name] = {
            "cv_accuracy": round(float(scores["test_accuracy"].mean()), 4),
            "cv_f1_macro": round(float(scores["test_f1_macro"].mean()), 4),
            "fit_seconds": round(float(scores["fit_time"].mean()), 1),
        }
        logger.info("%s : %s", name, results[name])
    return results


def tune_logistic_regression(X, y) -> GridSearchCV:
    pipe = Pipeline([
        ("tfidf", base_vectorizer()),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ])
    grid = {
        "tfidf__ngram_range": [(1, 1), (1, 2)],
        "tfidf__max_features": [20000, 50000],
        "tfidf__sublinear_tf": [True, False],
        "clf__C": [1, 3, 10, 30, 100],
    }
    search = GridSearchCV(pipe, grid, cv=CV, scoring="f1_macro", n_jobs=-1, refit=True)
    search.fit(X, y)
    logger.info("Meilleurs paramètres : %s (F1 macro CV %.4f)", search.best_params_, search.best_score_)
    return search


def main() -> None:
    train = pd.read_csv(TRAIN_PATH)
    X, y = train["text"], train["label"]

    comparison = compare_algorithms(X, y)
    search = tune_logistic_regression(X, y)

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(search.best_estimator_.named_steps["tfidf"], VECTORIZER_PATH)
    joblib.dump(search.best_estimator_.named_steps["clf"], MODEL_PATH)

    REPORTS_DIR.mkdir(exist_ok=True)
    summary = {
        "algorithm_comparison_cv": comparison,
        "best_params": {k: str(v) for k, v in search.best_params_.items()},
        "best_cv_f1_macro": round(float(search.best_score_), 4),
    }
    (REPORTS_DIR / "training.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
