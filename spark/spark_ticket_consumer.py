""" spark-submit \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 \
spark/spark_ticket_consumer.py """
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import StructType, StringType

print(">>> SCRIPT STREAMING TICKETS + AGRÉGATIONS <<<")

# -------------------------------------------------------------------
# 1. SparkSession
# -------------------------------------------------------------------
spark = (
    SparkSession.builder
    .appName("ClientTicketsStreaming")
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints/client_tickets")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# -------------------------------------------------------------------
# 2. Lecture Kafka / Redpanda
# -------------------------------------------------------------------
kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "redpanda:9092")
    .option("subscribe", "client_tickets")
    .option("startingOffsets", "latest")
    .load()
)

# -------------------------------------------------------------------
# 3. Schéma JSON
# -------------------------------------------------------------------
ticket_schema = (
    StructType()
    .add("ticket_id", StringType())
    .add("client_id", StringType())
    .add("created_at", StringType())
    .add("request", StringType())
    .add("type", StringType())
    .add("priority", StringType())
)

# -------------------------------------------------------------------
# 4. Parsing Kafka
# -------------------------------------------------------------------
tickets_df = kafka_df.select(
    from_json(col("value").cast("string"), ticket_schema).alias("ticket")
).select("ticket.*")

# -------------------------------------------------------------------
# 5. Enrichissement métier
# -------------------------------------------------------------------
enriched_df = tickets_df.withColumn(
    "support_team",
    when(col("type") == "billing", "Finance")
    .when(col("type") == "technical", "Tech")
    .otherwise("Customer Care")
)

# ================================================================
# STREAM 1 — AFFICHAGE DES TICKETS (append, stateless)
# ================================================================

tickets_query = (
enriched_df.writeStream
.outputMode("append")
.format("console")
.option("truncate", False)
.option("checkpointLocation", "/tmp/checkpoints/client_tickets/raw")
.start()
) 

# -------------------------------------------------------------------
# 6. Attente
# -------------------------------------------------------------------
tickets_query.awaitTermination()
