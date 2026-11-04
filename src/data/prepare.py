"""Nettoie le CSV brut, puis crée un split train/test stratifié et reproductible."""
import pandas as pd
from sklearn.model_selection import train_test_split

from src.data.preprocessing import clean_text
from src.utils.config import (
    CLEAN_PATH,
    LABELS,
    RANDOM_STATE,
    RAW_PATH,
    TEST_PATH,
    TEST_SIZE,
    TRAIN_PATH,
)


def prepare(raw_path=RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(raw_path).rename(columns={"clean_comment": "text", "category": "label"})
    n_raw = len(df)
    df["text"] = df["text"].map(clean_text)
    df = df[df["text"].str.len() > 0]
    df = df[df["label"].isin(LABELS)]
    # Dédoublonner avant le split : un même texte des deux côtés gonflerait le score de test.
    df = df.drop_duplicates(subset="text").reset_index(drop=True)
    print(f"{n_raw} lignes brutes -> {len(df)} lignes propres")
    return df[["text", "label"]]


def split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return train_test_split(
        df, test_size=TEST_SIZE, stratify=df["label"], random_state=RANDOM_STATE
    )


if __name__ == "__main__":
    clean = prepare()
    counts = clean["label"].value_counts()
    assert len(clean) >= 1000 and counts.min() >= 300, "Dataset trop petit pour la spécification"
    train, test = split(clean)
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(CLEAN_PATH, index=False)
    train.to_csv(TRAIN_PATH, index=False)
    test.to_csv(TEST_PATH, index=False)
    print(f"Distribution :\n{counts}")
    print(f"Train : {len(train)} | Test : {len(test)}")
