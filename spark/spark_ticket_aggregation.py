from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, count
from pyspark.sql.types import StructType, StructField, StringType
import psycopg2

spark = SparkSession.builder.appName("TicketsAggregation").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

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

def write_atomic_snapshot(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    rows = batch_df.collect()

    conn = psycopg2.connect(
        host="postgres",
        dbname="ticketsdb",
        user="tickets",
        password="tickets"
    )

    cur = conn.cursor()

    try:
        cur.execute("BEGIN;")
        cur.execute("TRUNCATE TABLE tickets_aggregation;")

        for row in rows:
            cur.execute(
                "INSERT INTO tickets_aggregation (type, count) VALUES (%s, %s)",
                (row["type"], row["count"])
            )

        cur.execute("COMMIT;")

    except Exception:
        cur.execute("ROLLBACK;")
        raise
    finally:
        cur.close()
        conn.close()

(
    agg_df.writeStream
    .outputMode("complete")
    .foreachBatch(write_atomic_snapshot)
    .option("checkpointLocation", "/tmp/checkpoints/tickets_aggregation")
    .start()
)

spark.streams.awaitAnyTermination()
