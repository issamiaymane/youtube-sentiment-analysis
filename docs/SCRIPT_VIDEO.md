# Script de la vidéo de démonstration (5-8 min)

Le TP demande : installation de l'extension, utilisation sur une vraie vidéo YouTube, toutes les fonctionnalités (filtres, dark mode, etc.), appel à l'API et temps de réponse.

## Avant d'enregistrer

- Lancer l'API : `docker run --rm -p 7860:7860 yt-sentiment` (ou `uvicorn app_api:app --port 7860`).
- Vérifier que l'extension pointe vers `http://localhost:7860` (bouton ⚙).
- Retirer l'extension de `chrome://extensions` si elle est déjà chargée (pour filmer l'installation).
- Préparer une vidéo YouTube en anglais avec beaucoup de commentaires (le modèle n'analyse que l'anglais).
- Fermer les notifications, agrandir le terminal et le navigateur.
- Enregistrer avec **Cmd + Maj + 5** → « Enregistrer tout l'écran », activer le micro dans « Options ».

## Déroulé

| Temps | Écran | À dire / montrer |
|---|---|---|
| 0:00 – 0:40 | README / `docs/architecture.svg` | Présentation : extension Chrome → API FastAPI → TF-IDF + régression logistique, 3 classes. |
| 0:40 – 1:30 | Terminal + `reports/figures/` | Modèle : accuracy 89,6 %, F1 0,82 / 0,94 / 0,90, matrice de confusion. |
| 1:30 – 2:45 | Terminal, puis `http://localhost:7860/docs` | `docker build` et `docker run`. Ouvrir `/health`, essayer `/predict_batch` dans Swagger : montrer la réponse et `processing_time_ms` (p95 1,3 ms pour 50 commentaires). |
| 2:45 – 3:30 | `chrome://extensions` | Mode développeur → « Charger l'extension non empaquetée » → dossier `chrome-extension/`. Épingler l'icône. |
| 3:30 – 5:00 | Vidéo YouTube | Ouvrir la vidéo, faire défiler un peu les commentaires, ouvrir l'extension → **Analyser**. Commenter les statistiques et la répartition. |
| 5:00 – 6:15 | Popup | Filtres **Tous / Positifs / Neutres / Négatifs**, bouton **◐** (thème sombre), **Copier**, **Exporter en CSV** (ouvrir le fichier). |
| 6:15 – 6:45 | Popup → ⚙ Réglages | URL de l'API ; arrêter le conteneur (Ctrl+C) et relancer l'analyse pour montrer le message d'erreur réseau, puis relancer l'API. |
| 6:45 – 7:30 | README | Limites (entraîné sur Reddit, négation, anglais seulement) et déploiement : Hugging Face puis Codespaces refusés (erreur 402), donc API locale ; la procédure Codespaces est prête dans le README. |

## Après

- Exporter en 1080p. Si le fichier est trop lourd pour un mail (> 25 Mo), le mettre sur Google Drive ou YouTube (non répertoriée) et mettre le lien dans le mail.
