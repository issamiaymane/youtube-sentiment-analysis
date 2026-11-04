"""Point d'entrée du déploiement : uvicorn app_api:app --host 0.0.0.0 --port 7860"""
from src.api.main import app

__all__ = ["app"]
