# Pipeline ETL Météo avec Airflow

Ce dépôt contient un Directed Acyclic Graph (DAG) Apache Airflow conçu pour extraire les données météorologiques actuelles de l'API Open-Meteo, les transformer et les charger dans une base de données PostgreSQL.

## Structure du Projet

* `etlweather.py` : Le fichier de définition principal du DAG Airflow.
* `docker-compose.yaml` : (Optionnel) Un fichier Docker Compose pour la mise en place d'une base de données PostgreSQL locale, si elle n'est pas gérée par un outil de distribution Airflow (comme Astro CLI).

## Fonctionnalités

* **Extraction** : Récupère les données météorologiques actuelles pour une latitude et une longitude spécifiées (par défaut Londres, Royaume-Uni) depuis l'API Open-Meteo.
* **Transformation** : Analyse la réponse JSON brute pour extraire les paramètres météorologiques pertinents tels que la température, la vitesse du vent, le code météo et l'horodatage.
* **Chargement** : Stocke les données météorologiques transformées dans une table `weather_data` d'une base de données PostgreSQL.
* **Planification** : Le DAG est planifié pour s'exécuter quotidiennement.

## Prérequis

Avant d'exécuter ce DAG, assurez-vous d'avoir les éléments suivants :

* **Docker** installé et en cours d'exécution sur votre système.
* Un environnement **Apache Airflow** configuré (par exemple, via Docker Compose, Astro CLI ou une installation locale).
* **Python 3.8+**
* Paquets Python requis : `apache-airflow`, `apache-airflow-providers-http`, `apache-airflow-providers-postgres`, `requests` (bien que `requests` puisse être implicitement géré par les dépendances de `HttpHook`, il est bon de le lister).

## Configuration

### 1. Configuration de la Base de Données (PostgreSQL)

Le DAG nécessite une base de données PostgreSQL pour stocker les données météorologiques.

Si vous utilisez Astro CLI ou un outil similaire qui gère votre base de données automatiquement, vous pouvez ignorer cette étape. Sinon, vous pouvez utiliser l'extrait de `docker-compose.yaml` fourni pour exécuter une instance PostgreSQL locale :

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    container_name: postgres_container
    environment:
      POSTGRES_USER: tsinjo
      POSTGRES_PASSWORD: nantosoa
      POSTGRES_DB: etl
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
    driver: local
