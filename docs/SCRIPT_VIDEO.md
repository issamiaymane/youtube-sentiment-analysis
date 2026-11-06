# Script de la vidéo de démonstration (5-8 min)

Le TP demande : installation de l'extension, utilisation sur une vraie vidéo YouTube, toutes les fonctionnalités (filtres, dark mode, etc.), appel à l'API et temps de réponse.

## Avant d'enregistrer

- Démarrer le Codespace, relancer `docker run -d -p 7860:7860 youtube-sentiment-api` et vérifier que le port 7860 est **public**.
- Vérifier que l'extension pointe vers `https://<nom>-7860.app.github.dev` (bouton ⚙).
- Retirer l'extension de `chrome://extensions` si elle est déjà chargée (pour filmer l'installation).
- Préparer une vidéo YouTube en anglais avec beaucoup de commentaires (le modèle n'analyse que l'anglais).
- Fermer les notifications, agrandir le terminal et le navigateur.
- Enregistrer avec **Cmd + Maj + 5** → « Enregistrer tout l'écran », activer le micro dans « Options ».

## Déroulé

| Temps | Écran | À dire / montrer |
|---|---|---|
| 0:00 – 0:40 | README / `docs/architecture.svg` | Présentation : extension Chrome → API FastAPI → TF-IDF + régression logistique, 3 classes. |
| 0:40 – 1:30 | Terminal + `reports/figures/` | Modèle : accuracy 89,6 %, F1 0,82 / 0,94 / 0,90, matrice de confusion. |
| 1:30 – 2:45 | Codespace, puis `https://<nom>-7860.app.github.dev/docs` | Déploiement : `docker build`, `docker run`, onglet Ports → 7860 public. Ouvrir `/health`, essayer `/predict_batch` dans Swagger : montrer la réponse et `processing_time_ms`. |
| 2:45 – 3:30 | `chrome://extensions` | Mode développeur → « Charger l'extension non empaquetée » → dossier `chrome-extension/`. Épingler l'icône. |
| 3:30 – 5:00 | Vidéo YouTube | Ouvrir la vidéo, faire défiler un peu les commentaires, ouvrir l'extension → **Analyser**. Commenter les statistiques et la répartition. |
| 5:00 – 6:15 | Popup | Filtres **Tous / Positifs / Neutres / Négatifs**, bouton **◐** (thème sombre), **Copier**, **Exporter en CSV** (ouvrir le fichier). |
| 6:15 – 6:45 | Popup → ⚙ Réglages | URL du Codespace ; passer le port en privé (ou `docker stop`) et relancer l'analyse pour montrer le message d'erreur réseau, puis rétablir. |
| 6:45 – 7:30 | README | Limites (entraîné sur Reddit, négation, anglais seulement) et hébergement éphémère : Codespaces convient à une démo, un PaaS serait nécessaire en production. |

## Après

- Exporter en 1080p. Si le fichier est trop lourd pour un mail (> 25 Mo), le mettre sur Google Drive ou YouTube (non répertoriée) et mettre le lien dans le mail.
