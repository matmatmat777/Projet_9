""" spark-submit \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 \
spark/spark_consumer_agg.py """


from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, count
from pyspark.sql.types import StructType, StringType

print(">>> STREAM 2 — AGRÉGATION CUMULÉE <<<")

spark = (
    SparkSession.builder
    .appName("TicketsAggregationStream")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "redpanda:9092")
    .option("subscribe", "client_tickets")
    .option("startingOffsets", "latest")
    .load()
)

schema = (
    StructType()
    .add("ticket_id", StringType())
    .add("client_id", StringType())
    .add("created_at", StringType())
    .add("request", StringType())
    .add("type", StringType())
    .add("priority", StringType())
)

tickets_df = kafka_df.select(
    from_json(col("value").cast("string"), schema).alias("ticket")
).select("ticket.*")

agg_df = (
    tickets_df
    .groupBy("type")
    .agg(count("*").alias("ticket_count"))
)

query = (
    agg_df.writeStream
    .format("console")
    .outputMode("complete")   # cumul global
    .option("truncate", False)
    .start()
)

query.awaitTermination()
