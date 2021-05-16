

# Airflow ETL for data processing 

PoC project is for deploying an ETL pipeline using Airflow for processing data from two different input files and then further preprocess, transform and generate output file in separate location with required columns and format.


## Solution Overview  

Entire solution has been containarized using dockers, docker-compose for spinning up containers, defining dependencies and enabling the Airflow cluster and dependencies for running ETL pipeline. 

```sh build.sh``` command will created images for development environment. Once images are build locally, ```docker-compose.yml``` will launch development environments, defining dependencies as separate containers. Airflow DAG `etl_dataprocessing_job ` is defined at path ```./mnt/airflow/dags/dataengineering_pipeline.py``` which initially waits for the respective files to be available at the input folder using FileSensor operator and once available it proceeds further triggering the task for Spark-submit job deploying application to be executed in spark-cluster. 

Above ETL pipeline can be processed using a PythonOperator but then considering the job needs to be scalable and flexible to process increasing volume of input source files, decided to use spark task for the data processing. For the sake of PoC input files are being read from local filepath, but pyspark job is enabled with required jars for working with S3/ Hadoop filesystems and output file generated would be put into `./output` folder. 

_facing some issues to deploy the spark application to cluster using Airflow SparkSubmitOperator, hence using Bash Operator with spark-submit for deploying the application to run in spark-cluster_.

  
- Architecture Components 
  - Airflow (version:1.10.12) configured with CeleryExecutor with all components (scheduler, webserver and executor) on different machines. _(image build replicating from https://github.com/puckel/docker-airflow and adding further dependencies)_. 
  - Postgres db to store Airflow metadata. 
  - Redis as Celery broker. 
  - Spark cluster (spark version:3.0 with hadoop:3.2, including all required jars for working with s3 filesystem) with 2 workers enabled.   
  - flower for monitoring celery workers


## Steps to lauch the components and triggering Airflow DAG for data processing :
  
  Clone repo and build images running below command
  
 ``` 
    sh build.sh 
 ``` 
  Above command would build the respective images for `airflow`, `celery-workers`, `spark master`, `worker nodes` based on base images. 

  Once images available locally, launch containers using `docker-compose.yml` for the development environment. 

 ``` 
    docker-compose up -d
 ``` 
 
Above docker-compose command will spin-up clusters as below : 
  - airflow_etl_pipeline_postgres_1
  - airflow_etl_pipeline_redis_1
  - airflow-webserver 
  - airflow-scheduler                    
  - celery-flower                  
  - celery-worker
  - spark-master             
  - spark-worker-2                 
  - spark-worker-1    

_incase of any issues launching the containers, please check for the ports mapped locally, as airflow, celery-flower and spark-master ports are mapped to host ports on 8085, 5555, 8080 respectively_. 

Once containers are up application UIs can be accessed as below from host machine :   
  - Airflow enabled with celery executor can be accessed at - http://localhost:8085/
  - Flower dashboard for celery workers can be accessed at - http://localhost:5555/
  - Spark cluster UI can be accessed at - http://localhost:8080/

Once in Airflow UI, add below file connections navigating to ```Admin --> Connections ```, as these file path connections are required in DAG for Filesensor tasks. 
 ```
    -  Conn Id    = file_path_source1
       Conn Type  = File
       Extra      = {"path":"/usr/local/airflow/data/input_source_1"}
    
    -  Conn Id    = file_path_source2
       Conn Type  = File
       Extra      = {"path":"/usr/local/airflow/data/input_source_2"}
 ```              

After adding above connections, you can trigger  the ```DAG: etl_dataprocessing_job ``` from Airflow UI. DAG is scheduled to run everyday at 1am and the filesensor task for input data.json file waits for two hours as its expected to arrive before 3am and filesensor task for engagement.csv file would timesout after 4 hours, which expects file to arrive before 5am, poking file at path for every 30 sec. Once both files are available, DAG proceeds further triggering pyspark script (./mnt/scripts/etl_process.py) for processing on spark cluster master ```spark://spark-master:7077```. 

On successful completion of etl pipeline DAG generates an output file for corresponding execution dates at output path - ```/usr/local/airflow/data/output ``` in .csv format mounted on local machine at - `./data/output/`.



## Tests scripts

```

docker exec -it celery-worker bash -c '$SPARK_HOME/bin/spark-submit --master spark://spark-master:7077 --num-executors 2 --name spark-cluster-job2 \
                                                                    --conf spark.executor.instances=2 \
                                                                    /usr/local/airflow/scripts/etl_process.py \
                                                                    --datafile  input_source_1/data_20210124.json \
                                                                    --engagementfile input_source_2/engagement_20210124.json \
                                                                    --execution_date 2021-01-24 00:00:00T 00:00:00+00:00'

```