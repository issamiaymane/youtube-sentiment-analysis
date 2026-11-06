# Documentation de l'API

URL de base : `http://localhost:7860` en local, ou `https://<nom>-7860.app.github.dev` une fois déployée dans GitHub Codespaces (voir le README). La page d'accueil `/` permet de tester le modèle, et la documentation interactive est sur `/docs`.

## GET /health

Vérifie l'état de l'API et du modèle.

```bash
curl http://localhost:7860/health
```

```json
{"status": "ok", "model_loaded": true, "version": "1.0.0"}
```

Renvoie `503` avec `"status": "unavailable"` si le modèle n'a pas pu être chargé.

## POST /predict_batch

Analyse de 1 à 500 commentaires de 10 000 caractères maximum chacun.

```bash
curl -X POST http://localhost:7860/predict_batch \
  -H "Content-Type: application/json" \
  -d '{"comments": ["This video is amazing!", "Worst tutorial ever"]}'
```

```json
{
  "predictions": [
    {"text": "This video is amazing!", "label": 1, "sentiment": "positif", "confidence": 0.9992},
    {"text": "Worst tutorial ever", "label": -1, "sentiment": "negatif", "confidence": 0.9991}
  ],
  "statistics": {
    "total": 2,
    "counts": {"negatif": 1, "neutre": 0, "positif": 1},
    "percentages": {"negatif": 50.0, "neutre": 0.0, "positif": 50.0},
    "average_confidence": 0.9992
  },
  "processing_time_ms": 1.9
}
```

- `label` vaut `-1` (négatif), `0` (neutre) ou `1` (positif).
- `confidence` est la probabilité de la classe prédite.
- Un texte vide après nettoyage (emoji inconnu, alphabet non latin) est renvoyé en neutre avec `confidence: 0`.

## Codes d'erreur

| Code | Cause |
|---|---|
| 422 | Batch vide ou de plus de 500 commentaires, type invalide, JSON mal formé, commentaire trop long |
| 503 | Modèle indisponible |
| 500 | Erreur interne (détail dans les logs) |

## CORS

Seules les origines `chrome-extension://` sont autorisées, avec les méthodes GET et POST.
