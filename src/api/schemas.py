"""Schémas Pydantic des requêtes et réponses."""
from pydantic import BaseModel, ConfigDict, Field

MAX_BATCH_SIZE = 500
MAX_COMMENT_LENGTH = 10000  # Limite de longueur d'un commentaire YouTube.


class BatchRequest(BaseModel):
    comments: list[str] = Field(
        min_length=1,
        max_length=MAX_BATCH_SIZE,
        examples=[["This video is amazing!", "Worst tutorial ever", "What camera do you use?"]],
    )


class Prediction(BaseModel):
    text: str
    label: int = Field(description="-1 négatif, 0 neutre, 1 positif")
    sentiment: str
    confidence: float = Field(description="Probabilité de la classe prédite ; 0 si texte vide après nettoyage")


class Statistics(BaseModel):
    total: int
    counts: dict[str, int]
    percentages: dict[str, float]
    average_confidence: float


class BatchResponse(BaseModel):
    predictions: list[Prediction]
    statistics: Statistics
    processing_time_ms: float


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    version: str
