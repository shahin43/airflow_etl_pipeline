# -- Software Stack Version

SPARK_VERSION="3.0.2"
HADOOP_VERSION="3.2"

# -- Building the Images - Spark cluster
docker build \
  -f docker/spark/sparkcluster_baseImage.Dockerfile \
  -t cluster-base .


docker build \
  --build-arg spark_version="${SPARK_VERSION}" \
  --build-arg hadoop_version="${HADOOP_VERSION}" \
  -f docker/spark/sparkbase.Dockerfile \
  -t spark-base .


docker build \
  -f docker/spark/spark-master.Dockerfile \
  -t spark-master .


docker build \
  -f docker/spark/spark-worker.Dockerfile \
  -t spark-worker .


# -- Building the Images - Airflow
docker build \
  -f docker/airflow/Dockerfile \
  -t airflow-base .