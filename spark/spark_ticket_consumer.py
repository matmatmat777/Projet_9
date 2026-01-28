from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import StructType, StringType

print(">>> STREAM — CONSUMER TICKETS POSTGRES <<<")

# -------------------------------------------------------------------
# Spark Session
# -------------------------------------------------------------------
spark = (
    SparkSession.builder
    .appName("ClientTicketsStreaming")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# -------------------------------------------------------------------
# Kafka source
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
# JSON schema
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

tickets_df = (
    kafka_df
    .select(from_json(col("value").cast("string"), ticket_schema).alias("ticket"))
    .select("ticket.*")
)

# -------------------------------------------------------------------
# Business enrichment
# -------------------------------------------------------------------
enriched_df = tickets_df.withColumn(
    "support_team",
    when(col("type") == "incident", "Support Technique")
    .when(col("type") == "demande", "Customer Care")
    .otherwise("Support Information")
)

# -------------------------------------------------------------------
# Console stream (debug)
# -------------------------------------------------------------------
console_query = (
    enriched_df.writeStream
    .outputMode("append")
    .format("console")
    .option("truncate", False)
    .option("checkpointLocation", "/tmp/checkpoints/client_tickets/console")
    .start()
)

# -------------------------------------------------------------------
# PostgreSQL writer
# -------------------------------------------------------------------
def write_to_postgres(batch_df, batch_id):
    if batch_df.rdd.isEmpty():
        return

    (
        batch_df.write
        .format("jdbc")
        .option("url", "jdbc:postgresql://postgres:5432/ticketsdb")
        .option("dbtable", "tickets")
        .option("user", "tickets")
        .option("password", "tickets")
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )

postgres_query = (
    enriched_df.writeStream
    .foreachBatch(write_to_postgres)
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/client_tickets/postgres")
    .start()
)

spark.streams.awaitAnyTermination()
