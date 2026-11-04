FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Les dépendances d'abord : modifier le code n'invalide pas cette couche du cache.
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY app_api.py .
COPY src/__init__.py src/__init__.py
COPY src/api src/api
COPY src/utils src/utils
COPY src/data/__init__.py src/data/preprocessing.py src/data/
COPY models/model.joblib models/vectorizer.joblib models/

# Hugging Face exécute les conteneurs avec l'UID 1000.
RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
  CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:7860/health', timeout=3)"

CMD ["uvicorn", "app_api:app", "--host", "0.0.0.0", "--port", "7860"]
