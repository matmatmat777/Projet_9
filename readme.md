# 📊 POC – Gestion de tickets clients avec Redpanda et PySpark

## Contexte

Dans le cadre de l’exercice 2, InduTech souhaite réaliser un **POC (Proof Of Concept)** afin de démontrer la mise en place d’un pipeline de données temps réel pour la gestion de tickets clients.

Les tickets sont générés en continu et ingérés via **Redpanda (Kafka-compatible)**, puis traités et analysés en **temps réel avec PySpark**.

Ce projet simule une architecture moderne orientée streaming, telle qu’elle pourrait être déployée dans un environnement cloud (AWS).

---

## Objectifs du projet

- Configurer un cluster **Redpanda** pour l’ingestion de données temps réel
- Produire des tickets clients aléatoires via un **script Python**
- Consommer et transformer ces données avec **PySpark Structured Streaming**
- Générer des **insights temps réel**
- Orchestrer l’ensemble avec **Docker Compose**

---

## Données manipulées

Chaque ticket client contient les champs suivants :

- `ticket_id` : identifiant unique du ticket
- `client_id` : identifiant du client
- `created_at` : date et heure de création
- `request` : description de la demande
- `type` : type de demande (`incident`, `demande`, `question`)
- `priority` : priorité (`low`, `medium`, `high`)

---

## Architecture du pipeline

<p align="center">
  <img src="media/Diagrammeexercice2.drawio.png" alt="Diagramme du pipeline ETL" width="900"/>
</p>

flowchart LR
    Producer[Python Producer] -->|Kafka| Redpanda[(Redpanda)]
    Redpanda --> SparkConsumer[PySpark Streaming]
    Redpanda --> SparkAgg[PySpark Aggregations]
    SparkConsumer --> ConsoleLogs[Affichage temps réel]
    SparkAgg --> ConsoleAgg[Agrégations temps réel]

## Description des composants

### 🔹 Redpanda
- Broker Kafka-compatible
- Réception des tickets en temps réel
- Exposé sur le port **9092**

### 🔹 Producer (Python)
- Génère des tickets clients aléatoires en continu
- Envoie les messages dans le topic **`client_tickets`**
- Implémenté avec la librairie **kafka-python**

### 🔹 Spark Consumer
- Lecture du topic Kafka en **Structured Streaming**
- Parsing des messages JSON
- Enrichissement des tickets avec une équipe de support :
  - `incident` → Support Technique  
  - `demande` → Customer Care  
  - `question` → Support Information
- Affichage des tickets enrichis en console

### 🔹 Spark Consumer Aggregation
- Traitement d’agrégation en temps réel
- Calcul du **nombre de tickets par type**
- Affichage des résultats à chaque micro-batch

### 🔹 Redpanda Console
- Interface web pour visualiser les topics et les messages Kafka
- Accessible via : **http://localhost:8080**

---

## Lancement du projet

### Prérequis
- Docker
- Docker Compose
- Environnement Linux / **WSL recommandé**

### Commande de démarrage
```bash
docker compose up --build

## Services démarrés

Les services suivants sont automatiquement lancés via Docker Compose :

- Redpanda
- Redpanda Console
- Producer
- Spark Consumer
- Spark Consumer Aggregation

---

## Accès aux interfaces

- **Redpanda Console** : http://localhost:8080

- **Spark UI** (si actif) :
  - Consumer : http://localhost:4040
  - Aggregation : http://localhost:4041

---

## Résultats observables

- Flux de tickets affichés en temps réel dans les logs Spark
- Agrégations mises à jour à chaque micro-batch
- Messages visibles dans Redpanda Console
- Pipeline stable et fonctionnel en continu

---

## Technologies utilisées

- Python 3
- Redpanda
- Apache Spark 3.4 (Structured Streaming)
- Kafka API
- Docker & Docker Compose
- Mermaid

---

## Limites et perspectives

### Limites
- Pas de persistance long terme (Data Lake ou base analytique)
- Pas de checkpoint Spark configuré (POC volontairement simplifié)

### Perspectives
- Ajout d’un stockage **Parquet** ou **S3**
- Mise en place de checkpoints Spark
- Ajout d’un dashboard de visualisation (Grafana, Superset)
- Déploiement cloud (AWS MSK / EKS)

---

## Démonstration vidéo

Une courte vidéo de démonstration accompagne ce projet et présente :
- Le lancement du pipeline
- L’ingestion des tickets
- Les traitements Spark en temps réel

📹 **[![Démonstration du pipeline](https://cdn.loom.com/sessions/thumbnails/b77b8b460e284563b798f538fdab5176-with-play.gif)](https://www.loom.com/share/b77b8b460e284563b798f538fdab5176)**
