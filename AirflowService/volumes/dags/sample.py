from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta

# Define default_args dictionary to specify the default parameters of the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 1),  # Ensure start_date is provided
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the PythonOperator task
def print_hello():
    print("Hello, Airflow!")

# Instantiate a DAG with the default_args
dag = DAG(
    'hello_airflow',
    default_args=default_args,
    description='A simple DAG to test Airflow',
    schedule_interval=timedelta(days=1),
)

# Define tasks
dag_start = DummyOperator(
    task_id='dag_start',
    dag=dag  # Associate the task with the DAG
)

dag_end = DummyOperator(
    task_id='dag_end',
    dag=dag  # Associate the task with the DAG
)

hello_task = PythonOperator(
    task_id='hello_task',
    python_callable=print_hello,
    dag=dag  # Associate the task with the DAG
)

# Set the task dependencies
dag_start >> hello_task >> dag_end