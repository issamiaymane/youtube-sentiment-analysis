"""Télécharge le dataset Reddit dans data/raw/reddit.csv et affiche ses statistiques."""
import pandas as pd
import requests

from src.utils.config import DATA_URL, RAW_PATH


def download(url: str = DATA_URL, path=RAW_PATH) -> None:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)


def print_stats(path=RAW_PATH) -> None:
    df = pd.read_csv(path)
    print(f"Fichier : {path}")
    print(f"Colonnes : {list(df.columns)}")
    print(f"Nombre de commentaires : {len(df)}")
    print(f"Valeurs manquantes :\n{df.isna().sum()}")
    label_col = df.columns[-1]
    print(f"Distribution des labels :\n{df[label_col].value_counts()}")


if __name__ == "__main__":
    download()
    print_stats()
