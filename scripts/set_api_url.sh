#!/usr/bin/env bash
# Pointe l'extension vers l'API publique du Codespace, puis recrée dist/chrome-extension.zip.
# Usage : scripts/set_api_url.sh https://NOM-7860.app.github.dev
set -euo pipefail

cd "$(dirname "$0")/.."
URL="${1:?Usage : scripts/set_api_url.sh https://NOM-7860.app.github.dev}"
URL="${URL%/}"
if [[ ! "$URL" =~ ^https://[a-z0-9-]+\.app\.github\.dev$ && "$URL" != "http://localhost:7860" ]]; then
  echo "URL refusée : https://NOM-7860.app.github.dev ou http://localhost:7860 attendue." >&2
  exit 1
fi

sed -i.bak -E "s#^const DEFAULT_API_URL = .*#const DEFAULT_API_URL = \"$URL\";#" chrome-extension/config.js
rm chrome-extension/config.js.bak
scripts/package_extension.sh
echo "Extension configurée pour $URL"
