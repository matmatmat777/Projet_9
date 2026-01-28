FROM apache/spark:3.4.1

USER root

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# PostgreSQL JDBC driver
ADD https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar /opt/spark/jars/

WORKDIR /app
COPY spark_ticket_consumer.py .
COPY spark_ticket_aggregation.py .
