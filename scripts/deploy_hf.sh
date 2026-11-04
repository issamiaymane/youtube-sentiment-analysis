#!/usr/bin/env bash
# Déploie l'API sur un Space Hugging Face, puis pointe l'extension vers son URL.
# Usage : hf auth login && scripts/deploy_hf.sh UTILISATEUR/NOM_DU_SPACE
set -euo pipefail

SPACE="${1:?Usage : scripts/deploy_hf.sh UTILISATEUR/NOM_DU_SPACE}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT

cd "$ROOT"
mkdir -p "$BUILD/src/data" "$BUILD/models"
cp Dockerfile .dockerignore requirements-prod.txt app_api.py "$BUILD/"
cp src/__init__.py "$BUILD/src/"
cp -R src/api src/utils "$BUILD/src/"
cp src/data/__init__.py src/data/preprocessing.py "$BUILD/src/data/"
cp models/model.joblib models/vectorizer.joblib "$BUILD/models/"
find "$BUILD" -name __pycache__ -type d -prune -exec rm -rf {} +

cat > "$BUILD/README.md" <<CARD
---
title: YouTube Sentiment API
emoji: 🎬
colorFrom: red
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

API FastAPI d'analyse de sentiment des commentaires YouTube. Documentation : /docs
CARD

hf repos create "$SPACE" --type space --space-sdk docker --exist-ok
hf upload "$SPACE" "$BUILD" . --repo-type space --commit-message "Déploiement de l'API"

# Les points et les majuscules sont normalisés dans le sous-domaine d'un Space.
SLUG="$(echo "${SPACE/\//-}" | tr '[:upper:]_.' '[:lower:]--')"
URL="https://$SLUG.hf.space"
sed -i.bak "s|^const DEFAULT_API_URL = .*|const DEFAULT_API_URL = \"$URL\";|" chrome-extension/config.js
rm chrome-extension/config.js.bak

# Extension packagée, avec l'URL de production.
mkdir -p dist
rm -f dist/chrome-extension.zip
(cd chrome-extension && zip -qr ../dist/chrome-extension.zip . -x '.*')

echo "Space : https://huggingface.co/spaces/$SPACE"
echo "API   : $URL"
echo "Paquet : dist/chrome-extension.zip"
echo "Rechargez l'extension dans chrome://extensions, puis vérifiez : curl $URL/health"
