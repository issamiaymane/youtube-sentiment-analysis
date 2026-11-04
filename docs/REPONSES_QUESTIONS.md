# Réponses aux questions de réflexion

## Phase 1 : environnement

**Pourquoi séparer les données raw et processed ?** Les données brutes restent intactes et servent de référence. Si le nettoyage change ou contient une erreur, on relance le script sans retélécharger, et on peut toujours reproduire le résultat.

**Quels fichiers ne doivent jamais être commités ?** Les secrets (`.env`, clés, tokens), l'environnement virtuel, les caches Python, les logs et les fichiers propres à la machine. Ici, les données sont aussi exclues car les scripts les régénèrent.

**Quelle est l'importance d'un environnement virtuel ?** Il isole les versions de chaque projet et évite les conflits. Avec des versions figées, l'entraînement et la production utilisent le même scikit-learn, ce qui compte car un modèle `joblib` est lié à sa version.

## Phase 2 : données

**Pourquoi nettoyer les URLs et mentions ?** Elles ne disent rien du sentiment. Elles ajoutent des milliers de termes rares au vocabulaire, ce qui favorise le surapprentissage.

**Comment gérer les emojis ?** Le dataset Reddit n'en contient pas, le modèle n'a donc rien appris sur eux, alors qu'ils sont fréquents sur YouTube. Les plus courants sont traduits en mots connus (🔥 devient `great`, 😭 devient `sad`). Les autres sont supprimés.

**Quel ratio train/test ?** 80/20, stratifié. Avec 36 450 commentaires, les 7 290 du test suffisent pour une estimation stable, et la stratification garde la même proportion de classes des deux côtés.

## Phase 3 : modèle

**Pourquoi TF-IDF plutôt que Count Vectorizer ?** TF-IDF réduit le poids des mots présents partout (`the`, `is`) et valorise les mots plus discriminants. Il atténue aussi l'effet de la longueur du texte, très variable ici.

**Comment interpréter la matrice de confusion ?** Chaque ligne est une vraie classe et chaque colonne une prédiction ; la diagonale compte les réussites. Ici, l'erreur principale est la confusion négatif/positif (205 négatifs prédits positifs, 226 positifs prédits négatifs), alors que le neutre est très bien reconnu.

**Quels hyperparamètres ont le plus d'impact ?** Mesuré en changeant un seul paramètre à partir du meilleur modèle (F1 macro de 0,868 en validation croisée) :

| Changement | F1 macro |
|---|---|
| `C` = 1 au lieu de 30 | 0,834 |
| Bigrammes au lieu d'unigrammes | 0,856 |
| `sublinear_tf` désactivé | 0,862 |
| `C` = 100 au lieu de 30 | 0,864 |
| 50 000 termes au lieu de 20 000 | 0,868 |

`C` a le plus d'impact, suivi des n-grammes. Passer à 50 000 termes ne change rien, on garde donc le modèle le plus léger.

## Phase 4 : API

**Pourquoi FastAPI plutôt que Flask ?** La validation Pydantic et la documentation `/docs` sont intégrées, ce qui évite d'écrire ce code à la main. FastAPI gère aussi nativement l'asynchrone.

**À quoi sert CORS ?** Le navigateur bloque par défaut les requêtes JavaScript vers une autre origine. CORS indique quelles origines sont autorisées, ici uniquement les extensions Chrome.

**Comment gérer le chargement du modèle ?** Une seule fois au démarrage, dans le `lifespan` de FastAPI, puis en mémoire. Le charger à chaque requête serait bien trop lent. Si le chargement échoue, `/health` renvoie 503.

## Phase 5 : extension

**Comment gérer les réponses (threads) ?** Le fil principal et les réponses déjà visibles sont extraits. Les réponses sont repérées grâce à leur conteneur `#replies` et marquées `↳`. Les réponses repliées ne sont pas chargées.

**Quelle stratégie pour les commentaires dynamiques ?** YouTube les charge au défilement. Le content script fait défiler la page jusqu'au nombre demandé, s'arrête après environ 5 secondes sans nouveauté, puis rend à l'utilisateur sa position.

**Comment optimiser avec de nombreux commentaires ?** Envoi par batchs de 100, affichage limité à 300 lignes, et dédoublonnage par auteur et texte.

## Phase 6 : déploiement

**Pourquoi séparer les requirements dev et prod ?** L'image n'a besoin ni de pandas, ni de matplotlib, ni de pytest. Moins de paquets signifie une image plus petite, un build plus rapide et une surface d'attaque réduite.

**Comment réduire la taille de l'image ?** Image `slim`, dépendances de production uniquement, `--no-cache-dir`, et copie des seuls fichiers utiles grâce au `.dockerignore`.

**Quelle stratégie pour les mises à jour du modèle ?** Réentraîner, vérifier les critères avec `evaluate` et les tests, puis redéployer avec le script. Le dépôt du Space garde l'historique, ce qui permet de revenir en arrière. Il serait utile d'ajouter ensuite une version du modèle dans `/health`.
