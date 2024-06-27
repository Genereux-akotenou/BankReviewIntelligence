from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# UTILS
# ---------------------------------------------------------------------------------
def run_crawler():
    import subprocess
    result = subprocess.run(['python3', '/Users/genereux/Documents/UM6P/COURS-S2/BI_KD/BankReviewIntelligence/ScrapperService/production_standalone/scrapper_initialize.py'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print('>>>>>>>>>ERROR<<<<<<<<<')
        print(result.stderr)

# DAG
# ---------------------------------------------------------------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
dag = DAG(
    'INITIAL-DATA-CRAWLER',
    default_args=default_args,
    description='Retrieve initial data',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
)

# PYTHON OPERATOR
# ---------------------------------------------------------------------------------
run_script_task = PythonOperator(
    task_id='run_script',
    python_callable=run_crawler,
    dag=dag,
)

# ORCHESTRATION
# ---------------------------------------------------------------------------------
run_script_task
