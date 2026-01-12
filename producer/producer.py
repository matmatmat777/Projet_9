import json
import time
import uuid
import random
import os
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# Configuration Redpanda (Kafka-compatible)
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
TOPIC_NAME = "client_tickets"

# Attente active de Redpanda (indispensable en Docker)
producer = None
for attempt in range(10):
    try:
        print(f"⏳ Connexion à Kafka (tentative {attempt + 1}/10)...")
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=5,
            linger_ms=100
        )
        print("✅ Connexion à Kafka réussie")
        break
    except NoBrokersAvailable:
        print("❌ Kafka indisponible, nouvelle tentative dans 2s...")
        time.sleep(2)

if producer is None:
    raise RuntimeError("🚨 Impossible de se connecter à Kafka (Redpanda)")

TICKET_TYPES = ["incident", "demande", "question"]
PRIORITIES = ["low", "medium", "high"]
REQUESTS = [
    "Problème de connexion",
    "Erreur application",
    "Demande d'information",
    "Bug après mise à jour",
    "Accès refusé"
]

def generate_ticket():
    """
    Génère un ticket client aléatoire
    """
    return {
        "ticket_id": str(uuid.uuid4()),
        "client_id": random.randint(1000, 9999),
        "created_at": datetime.utcnow().isoformat(),
        "request": random.choice(REQUESTS),
        "type": random.choice(TICKET_TYPES),
        "priority": random.choice(PRIORITIES)
    }

def produce_tickets(interval_seconds=2):
    """
    Envoie des tickets en continu dans Redpanda
    """
    print("🚀 Producteur de tickets démarré...")
    while True:
        ticket = generate_ticket()
        producer.send(TOPIC_NAME, ticket)
        producer.flush()
        print(f"📨 Ticket envoyé : {ticket}")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    produce_tickets()
