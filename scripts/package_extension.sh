#!/usr/bin/env bash
# Crée dist/chrome-extension.zip, avec l'URL d'API de config.js.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p dist
rm -f dist/chrome-extension.zip
(cd chrome-extension && zip -qr ../dist/chrome-extension.zip . -x '.*')
echo "dist/chrome-extension.zip"
