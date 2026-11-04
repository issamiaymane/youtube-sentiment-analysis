"""Application FastAPI : /health et /predict_batch."""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.predictor import SentimentPredictor, compute_statistics
from src.api.schemas import MAX_COMMENT_LENGTH, BatchRequest, BatchResponse, HealthResponse
from src.utils.logger import get_logger

logger = get_logger("api")
VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chargé une seule fois au démarrage, pas à chaque requête.
    try:
        app.state.predictor = SentimentPredictor()
        logger.info("Modèle chargé")
    except Exception:
        app.state.predictor = None
        logger.exception("Impossible de charger le modèle")
    yield


app = FastAPI(title="YouTube Sentiment API", version=VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^chrome-extension://[a-p]{32}$",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Erreur non gérée sur %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Erreur interne du serveur"})


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {"service": "YouTube Sentiment API", "docs": "/docs", "health": "/health"}


@app.get("/health", response_model=HealthResponse)
def health(request: Request) -> JSONResponse:
    loaded = request.app.state.predictor is not None
    return JSONResponse(
        status_code=200 if loaded else 503,
        content={"status": "ok" if loaded else "unavailable", "model_loaded": loaded, "version": VERSION},
    )


@app.post("/predict_batch", response_model=BatchResponse)
def predict_batch(body: BatchRequest, request: Request) -> dict:
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Modèle indisponible")
    if any(len(comment) > MAX_COMMENT_LENGTH for comment in body.comments):
        raise HTTPException(status_code=422, detail=f"Commentaire de plus de {MAX_COMMENT_LENGTH} caractères")

    start = time.perf_counter()
    predictions = predictor.predict(body.comments)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("Batch de %d commentaires traité en %.1f ms", len(body.comments), elapsed_ms)
    return {
        "predictions": predictions,
        "statistics": compute_statistics(predictions),
        "processing_time_ms": round(elapsed_ms, 2),
    }
