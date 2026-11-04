"""Chemins et constantes partagés par tout le projet."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA_URL = (
    "https://raw.githubusercontent.com/Himanshu-1703/"
    "reddit-sentiment-analysis/refs/heads/main/data/reddit.csv"
)
RAW_PATH = ROOT / "data" / "raw" / "reddit.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "clean.csv"
TRAIN_PATH = ROOT / "data" / "processed" / "train.csv"
TEST_PATH = ROOT / "data" / "processed" / "test.csv"

MODELS_DIR = ROOT / "models"
MODEL_PATH = MODELS_DIR / "model.joblib"
VECTORIZER_PATH = MODELS_DIR / "vectorizer.joblib"

REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
LOGS_DIR = ROOT / "logs"

RANDOM_STATE = 42
TEST_SIZE = 0.2
LABELS = [-1, 0, 1]
LABEL_NAMES = {-1: "negatif", 0: "neutre", 1: "positif"}
