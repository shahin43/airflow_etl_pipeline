# airflow_etl_pipeline

ETL data processing pipeline using Airflow. 
For solution overview and further details refer - `ETL_README.md`.  


### Setting up the environment : 
Git clone the repo to setup the environment and run data processing pipeline in Airflow 

```
   git clone https://github.com/shahin43/airflow_etl_pipeline.git  

```

Build the environment 
``` 
 sh build.sh 
``` 

And then, docker-compose for spinning up containers 
``` 
  docker-compose up -d
``` 


Once containers are up Airflow, Flower and Spark cluster can be accessed as below from host machine as below :   
  - Airflow enabled with celery executor can be accessed at - http://localhost:8085/
  - Flower dashboard for celery workers can be accessed at - http://localhost:5555/
  - Spark cluster UI can be accessed at - http://localhost:8080/