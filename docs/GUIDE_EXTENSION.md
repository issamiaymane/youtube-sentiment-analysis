# Guide de l'extension Chrome

## Installation

1. Décompresser `chrome-extension.zip`, ou utiliser directement le dossier `chrome-extension/`.
2. Ouvrir `chrome://extensions`.
3. Activer le **mode développeur**, en haut à droite.
4. Cliquer sur **Charger l'extension non empaquetée** et choisir le dossier.
5. Épingler l'extension depuis l'icône en forme de pièce de puzzle.

## Utilisation

1. Démarrer l'API locale : `uvicorn app_api:app --port 7860`, ou le conteneur Docker du README.
2. Ouvrir une vidéo YouTube.
3. Cliquer sur l'icône de l'extension.
4. Choisir le nombre de commentaires à analyser : 50, 100, 200 ou 500.
5. Cliquer sur **Analyser**. La page défile seule pour charger les commentaires, puis revient à sa position.

![Résultats](screenshots/popup_light.png)

## Fonctionnalités

| Fonction | Utilisation |
|---|---|
| Statistiques | Graphique et pourcentages par sentiment |
| Liste | Auteur, sentiment et confiance de chaque commentaire ; les réponses sont marquées `↳` |
| Filtres | Tous, Positifs, Neutres, Négatifs |
| Thème clair ou sombre | Clair par défaut, bouton `◐`, le choix est mémorisé |
| Copier | Copie le résumé et les commentaires du filtre actif |
| Exporter | Télécharge les commentaires du filtre actif en CSV |
| Choix de l'API | Bouton `⚙` : par défaut `http://localhost:7860` |

![Thème sombre](screenshots/popup_dark.png)

## Problèmes fréquents

| Message | Solution |
|---|---|
| Ouvrez une vidéo YouTube | L'onglet actif n'est pas une vidéo |
| Aucun commentaire trouvé | Commentaires désactivés, ou page pas encore chargée : réessayer |
| Impossible de joindre l'API | Démarrer l'API locale ou vérifier l'URL dans `⚙` |
| L'API ne répond pas après 60 s | Redémarrer l'API, puis réessayer |

![Erreur réseau](screenshots/popup_error.png)
