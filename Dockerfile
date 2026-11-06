FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=7860
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

# Utilisateur non root.
RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
  CMD python -c "import os, urllib.request as u; u.urlopen('http://127.0.0.1:%s/health' % os.environ['PORT'], timeout=3)"

# Forme shell pour que ${PORT} soit lu au démarrage (docker run -e PORT=8000 ...).
CMD ["sh", "-c", "exec uvicorn app_api:app --host 0.0.0.0 --port ${PORT}"]
