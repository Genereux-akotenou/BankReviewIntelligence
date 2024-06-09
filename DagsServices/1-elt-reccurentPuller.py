from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Define the Python function to be executed
def run_my_script():
    import subprocess
    result = subprocess.run(['python3', '/path/to/your/script.py'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'REVIEW-CROWLER-2DAYS',
    default_args=default_args,
    description='Dag to pull remaining review each 2 days',
    schedule_interval=timedelta(days=2),
    start_date=days_ago(1),
    catchup=False,
)

# Define the PythonOperator
run_script_task = PythonOperator(
    task_id='run_script',
    python_callable=run_my_script,
    dag=dag,
)

# Define the task dependencies
run_script_task
