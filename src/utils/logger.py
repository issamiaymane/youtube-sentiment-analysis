"""Logger commun : console + logs/app.log."""
import logging

from src.utils.config import LOGS_DIR


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)
    try:
        LOGS_DIR.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(LOGS_DIR / "app.log", encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError:
        pass  # Système de fichiers en lecture seule (conteneur) : console uniquement.
    return logger
