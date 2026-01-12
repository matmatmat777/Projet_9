FROM apache/spark:3.4.1

USER root

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

WORKDIR /app
COPY spark_consumer.py .
COPY spark_consumer_agg.py .
