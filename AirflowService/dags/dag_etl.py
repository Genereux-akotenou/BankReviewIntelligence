from airflow import DAG
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.operators.python_operator import PythonOperator
import pandas as pd
from datetime import timedelta, datetime
import glob 
import os
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

def extract_task():
    list_file = glob.glob(os.path.expanduser('~/input/*.csv'))
    file = list_file[0] 
    return file, pd.read_csv(file, sep=";").to_json(orient='records')

def transform_task(file, data):
    print("-------------transform_task-----------------------") 
    print(file)
    print(data[:100])
    print("-------------transform_task-----------------------") 
    df = pd.DataFrame(json.loads(data))
    def calculate_birth_year(age):
        birth_year = 2014 - age
        return birth_year
    df["year"] = df["age"].apply(calculate_birth_year)

    mean_job = df.groupby(['job'])["duration"].mean()
    mean_job_in_minute = mean_job / 60
    
    return file, pd.DataFrame(mean_job_in_minute).to_json(orient='records')

def load_task(file, data):
    print("-------------load_task-----------------------") 
    print(file)
    print(data[:100])
    print("-------------load_task-----------------------") 
    df = pd.DataFrame(json.loads(data))
    file_name = os.path.basename(file)
    parquet_file = os.path.expanduser(f'~/output/{file_name}_loaded.parquet')
    df.to_parquet(parquet_file)
    return file

def clean_up_task(file):
    print("-------------clean_up_task-----------------------") 
    print(file)
    print("-------------clean_up_task-----------------------") 
    os.rename(file, file + "_done_" + datetime.now().strftime('%Y%m%d%H%M%S'))

with DAG(
    dag_id='Simple_etl',
    start_date=datetime(2024, 2, 11),
    schedule_interval=None, # Run manually
    catchup=False,
    default_args=default_args,
) as dag:

    # Define the FileSensor task
    file_sensor = FileSensor(
        task_id='file_sensor',
        filepath=os.path.expanduser ('~/input/*.csv'),  
        poke_interval=10  
    )
 
    extract = PythonOperator(
        task_id='extract_task',
        python_callable=extract_task,
    )

    transform = PythonOperator(
        task_id='transform_task',
        python_callable=transform_task,
        provide_context=True,
        op_kwargs = {'file': '{{ ti.xcom_pull(task_ids="extract_task")[0] }}', 'data': '{{ ti.xcom_pull(task_ids="extract_task")[1] }}'}
    )

    load = PythonOperator(
        task_id='load_task',
        provide_context=True,
        python_callable=load_task,
        op_kwargs = {'file': '{{ ti.xcom_pull(task_ids="transform_task")[0] }}', 'data': '{{ ti.xcom_pull(task_ids="transform_task")[1] }}'}
    )

    clean_up = PythonOperator(
        task_id='clean_up_task',
        provide_context=True,
        python_callable=clean_up_task,
        op_kwargs = {'file': '{{ ti.xcom_pull(task_ids="load_task") }}'}
    )

    file_sensor >> extract >> transform >> load >> clean_up
