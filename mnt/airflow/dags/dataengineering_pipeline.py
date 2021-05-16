from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import datetime, timedelta
from airflow.models import Variable
from datetime import datetime



default_args = {
    'start_date': datetime(2021, 1, 24),
    'end_date': datetime(2021, 1, 26),
    'owner': 'ETL user',
    'email': 'etljobs@test.com'
}

def process(p1):
    print(p1)
    return 'done'

def define_filenames(ds, **kwargs):
    Variable.set('execution_date', kwargs['execution_date'])
    print(f"execution date is : {kwargs['execution_date']}")
    print(f""" in date format : { kwargs['execution_date'].strftime("%Y%m%d") } """)
    print(kwargs)
    kwargs['ti'].xcom_push(key='data_filename1', value=f'test_value.json' )
    dateformat = kwargs['execution_date'].strftime("%Y%m%d")
    kwargs['ti'].xcom_push(key='data_filename', value=f'data_{dateformat}.json' )
    kwargs['ti'].xcom_push(key='engagement_filename',value=f'engagement_{dateformat}.csv' )
    return True



with DAG(dag_id='etl_dataprocessing_job', schedule_interval='0 1 * * *', default_args=default_args, catchup=True) as dag:
    
    task_start = BashOperator(task_id='task_start', bash_command='echo "Pipeline starting !!"', depends_on_past=True, wait_for_downstream=True)

    files_to_check = PythonOperator(task_id='files_to_check', provide_context=True, python_callable=define_filenames )

    task_check_filenames = BashOperator(task_id='check_filenames', bash_command=""" echo " data filename is : {{ task_instance.xcom_pull(task_ids='files_to_check',key='data_filename' ) }} | engagement filename is : {{ task_instance.xcom_pull(task_ids='files_to_check',key='engagement_filename' ) }} "   """)


    # task_8 = BashOperator(task_id='task_8', bash_command=""" echo "command is : {{ task_instance.xcom_pull(task_ids='task_7',key='detect_filename' ) }}"  """)
    
    data_filesensor = FileSensor(
                   task_id="task_data_filesensor",
                   filepath="{{ task_instance.xcom_pull(task_ids='files_to_check',key='data_filename' ) }}",
                   fs_conn_id="file_path_source1",
                   poke_interval= 30,
                   timeout=7200
                )
    
    engagement_filesensor = FileSensor(
                   task_id="task_engagement_filesensor",
                   filepath="{{ task_instance.xcom_pull(task_ids='files_to_check',key='engagement_filename' ) }}",
                   fs_conn_id="file_path_source2",
                   poke_interval= 30,
                   timeout=14400
                )

    # data_processing = SparkSubmitOperator(
    #     task_id="data_processing",
    #     conn_id="spark_cluster",
    #     application="/usr/local/airflow/scripts/etl_process.py",
    #     verbose=True
    # )

    # Templated command with macros
    spark_submit_command="""   $SPARK_HOME/bin/spark-submit --master spark://spark-master:7077 --num-executors 2 \
                                    --name spark-cluster-job2  --conf spark.executor.instances=2 \
                                    /usr/local/airflow/scripts/etl_process.py \
                                    --datafile  input_source_1/{{ task_instance.xcom_pull(task_ids='files_to_check',key='data_filename' ) }}  \
                                    --engagementfile input_source_2/{{ task_instance.xcom_pull(task_ids='files_to_check',key='engagement_filename' ) }} \
                                    --execution_date {{ execution_date }} """

    # Show rates
    task_sparksubmit = BashOperator(
        task_id='task_sparksubmit',
        bash_command=spark_submit_command
    )

    task_finish = BashOperator(task_id='task_finish', bash_command='echo "Pipeline completed !!"')


    task_start >> files_to_check >> task_check_filenames >> [data_filesensor, engagement_filesensor]

    [data_filesensor, engagement_filesensor] >>  task_sparksubmit 

    task_sparksubmit >> task_finish
   

        