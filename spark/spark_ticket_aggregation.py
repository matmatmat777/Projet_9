from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, count
from pyspark.sql.types import StructType, StructField, StringType

print(">>> STREAM — AGRÉGATION TICKETS <<<")

spark = (
    SparkSession.builder
    .appName("TicketsAggregationStream")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "redpanda:9092")
    .option("subscribe", "client_tickets")
    .option("startingOffsets", "earliest")
    .load()
)

schema = StructType([
    StructField("ticket_id", StringType()),
    StructField("type", StringType())
])

tickets_df = (
    kafka_df
    .selectExpr("CAST(value AS STRING)")
    .select(from_json(col("value"), schema).alias("ticket"))
    .select("ticket.type")
    .filter(col("type").isNotNull())
)

agg_df = tickets_df.groupBy("type").count()

# =========================
# 1. CONSOLE (DÉMO)
# =========================
console_query = (
    agg_df.writeStream
    .outputMode("complete")
    .format("console")
    .option("truncate", False)
    .start()
)

# =========================
# 2. POSTGRES (PERSISTENCE)
# =========================
def write_to_postgres(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    print(f">>> WRITE POSTGRES BATCH {batch_id}")
    batch_df.show(truncate=False)

    (
        batch_df
        .coalesce(1)
        .write
        .format("jdbc")
        .option("url", "jdbc:postgresql://postgres:5432/ticketsdb")
        .option("dbtable", "tickets_aggregation")
        .option("user", "tickets")
        .option("password", "tickets")
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")   # SNAPSHOT
        .save()
    )

postgres_query = (
    agg_df.writeStream
    .outputMode("complete")
    .foreachBatch(write_to_postgres)
    .start()
)

spark.streams.awaitAnyTermination()
