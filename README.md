# Dépôts de brevets et marchés financiers (2017-2024)
## Décrypter la valeur de l'innovation française par la Classification Internationale des Brevets (CIB)

Ce projet de recherche explore la corrélation entre l'effort d'innovation technologique et la perception des marchés financiers. En utilisant la Classification Internationale des Brevets (CIB) comme pivot, nous analysons comment le dépôt de brevets agit comme un signal stratégique précoce (early signal) réduisant l'asymétrie d'information entre les entreprises et les investisseurs.

## Points clés de l'étude
Horizon temporel : 2017 - 2024.

Indicateur Amont : Flux de dépôts de brevets français (données INPI).

Indicateur Aval : Rendements boursiers des entreprises cotées sur Euronext Paris.

Cadre Méthodologique : Analyse économétrique (Lags optimaux, tests MCO, ARMA-GARCH).

## Structure du projet 

```text
.
├── data/              # Dossiers de données (non synchronisés sur Git)
├── notebooks/         # Notebooks Jupyter (Exploration & Modélisation)
├── scripts/           # Fonctions Python réutilisables (.py)
│   ├── importation.py # Pipeline de traitement des flux XML/S3
│   └── stats_des.py   # Visualisations et statistiques descriptives
├── .gitignore         # Fichiers à exclure (données, checkpoints)
├── requirements.txt   # Dépendances du projet
└── README.md          # Documentation principale
```

## Installation et Utilisation
1. Configuration de l'environnement

Le projet est optimisé pour l'écosystème Onyxia (SSP Cloud). Pour installer les bibliothèques nécessaires :

pip install -r requirements.txt

2. Accès aux données

Le projet croise deux sources hétérogènes :

Données INPI : Stockées sous format .parquet sur le stockage S3 du projet après un parsing initial des fichiers XML sources.

Données Financières : Extraites via l'API yfinance pour les tickers Euronext (ex: OR.PA, MC.PA).

Pour reproduire l'analyse, exécutez le fichier Main.ipynb. Ce dernier pilote les modules situés dans le répertoire scripts/ pour assurer la cohérence du pipeline.

## Méthodologie et Modélisation
Le pipeline d'analyse est automatisé pour permettre une étude multi-sectorielle (Automobile, Pharma, Tech, etc.) :

Nettoyage & Segmentation : Filtrage des types de brevets (A1) et regroupement par classes CIB.

Construction de Portefeuilles : Création d'indices boursiers sectoriels pondérés.

## Analyse Économétrique :

Tests de stationnarité (ADF).

Recherche de lags optimaux (impact des brevets à t−n sur les cours à t).

Validation des hypothèses MCO (Tests de White, Durbin-Watson, Jarque-Bera).

Prédiction : Comparaison de modèles ARMA, EWMA et GARCH pour évaluer la capacité prédictive du signal "Brevet".

## Résultats et Perspectives

Identification des secteurs où l'innovation est un prédicteur robuste de la valeur de marché.

Développement d'un indicateur de trading basé sur la croissance logarithmique des dépôts.