FROM apache/spark:3.4.1

USER root

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

WORKDIR /app
COPY spark_ticket_consumer.py .
COPY spark_ticket_aggregation.py .
