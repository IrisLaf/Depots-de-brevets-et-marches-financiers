# Dépôts de brevets et marchés financiers (2017-2024)

Ce projet de recherche explore la corrélation entre l'innovation technologique et la perception des marchés financiers. Après avoir récupéré des données sur les demandes de brevets déposées en France entre 2017 et 2024, nous étudions les secteurs les plus innovants à partir de la Classification Internationale des Brevets (CIB). Nous proposons ensuite une classification construite à partir de la CIB à laquelle on associe plusieurs portefeuilles d'entreprises cotées sur Euronext Paris. Cela nous permet d'analyser comment le dépôt de brevets est corrélé avec les rendements boursiers de ces entreprises. L'idée est de voir si ces demandes de brevets pourraient agir comme des signaux stratégiques précoces (early signal) réduisant l'asymétrie d'information entre les entreprises et les investisseurs. 

## Structure du projet 

```text
Projet-Python/
├── output/                   # Graphiques et résultats d'analyses
│   ├── heteroscedasticite_auto.png
│   └── normalite_residus_auto.png
├── scripts/                  # Modules Python réutilisables
│   ├── __init__.py
│   ├── cleaning.py           # Fonctions de nettoyage et filtrage des données CIB
│   ├── importation.py        # Fonctions d'importation (S3 & yfinance)
│   └── stats_des.py          # Fonctions de statistiques descriptives
├── .gitignore                # Fichiers à exclure (données, caches)
├── load_data.ipynb           # Notebook dédié au parsing initial
├── Main.ipynb                # Workflow principal et modélisation économétrique
├── README.md                 # Présentation du projet
└── requirements.txt          # Dépendances du projet
```

## Installation et Utilisation
### 1. Configuration de l'environnement

Le projet est optimisé pour l'écosystème Onyxia (SSP Cloud). Pour installer les bibliothèques nécessaires, la commande `pip install -r requirements.txt`(présente au début du fichier main) est nécessaire.
Pour reproduire l'analyse, exécutez le fichier [Main.ipynb](Main.ipynb). Ce dernier reprend des fonctions situées dans le dossier scripts/.

### 2. Accès aux données

Le projet utilise deux sources différentes :
- Les données des demandes de brevets de l'INPI. Elles sont obtenues à partir du [serveur FTP de l'INPI](https://data.inpi.fr/content/editorial/lien-serveur-ftp-PI) qui est accessible en complétant un questionnaire qui permettent d'obtenir les codes de connexion. Ces fichiers au format XML sont stockées dans un bucket S3. Après un parsing des fichiers, une base agrégée des différents fichiers est ensuite stockée au format parquet sur le stockage S3 du projet, pour éviter de devoir refaire tourner le code de parsing.
- Les données des cours d'action. Elles sont extraites via l'API [yfinance](https://ranaroussi.github.io/yfinance/reference/index.html) pour les tickers Euronext (ex: OR.PA, MC.PA).

## Méthodologie suivie

### 1. Récupération et traitement des données
Dans cette partie, nous importons les données des demandes de brevet de l'INPI. Puis nous réalisons un code de parsing pour exploiter les informations des fichiers .xml dans un dataframe panda et décrivons au mieux le contenu des variables. Enfin, nous nettoyons les données (gestion des NA et des valeurs incohérentes). 

### 2. Analyse descriptive
Ensuite, nous réalisons plusieurs statistiques descriptives sur :
1. L'évolution du nombre de demandes de brevet au cours du temps (2017-2024)
2. Les inventeurs et les déposants de brevet (qui sont-ils et d'oùu viennent-ils ?)
3. Les secteurs (au sens de la CIB) avec le plus de demandes de brevets

### 3. Modélisation
Enfin, nous proposons de mesurer l'effet du nombre de demandes de brevet au sein d'un secteur sur le cours d'action des entreprises cotées en bourse de ce secteur. Après avoir construit une classification, créé des portefeuilles d'entreprises pour cette classification et choisir des pondérations, nous réalisons une analyse économétrique qui comprend :
- Des tests de stationnarité (ADF).
- La recherche de lags optimaux (impact des brevets à t−n sur les cours à t).
- Des tests de validation des hypothèses MCO (Tests de White, Durbin-Watson, Jarque-Bera).
- Prédiction : Comparaison de modèles ARMA, EWMA et GARCH pour évaluer la capacité prédictive du signal "Brevet".

### 4. Résultats et Perspectives
**partie à rédiger**

Identification des secteurs où l'innovation est un prédicteur robuste de la valeur de marché.

Développement d'un indicateur de trading basé sur la croissance logarithmique des dépôts.