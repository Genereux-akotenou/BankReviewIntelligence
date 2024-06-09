from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import os
import pandas as pd
import importlib.util

# VARIABLES
# ---------------------------------------------------------------------------------
BASE_PATH           = "/Users/genereux/Documents/UM6P/COURS-S2/BI_KD/BankReviewIntelligence"
PARQUET_PATH        = BASE_PATH + "/ScrapperService/production_standalone/row_data/parcket"
MACRO_TABLE_PATH    = BASE_PATH + "/ScrapperService/production_standalone/macro_table"
PROCESS_SCRIPT_PATH = BASE_PATH + "/ProcessingService/01-parquet_preprocessing.py"

# UTILS
# ---------------------------------------------------------------------------------
def find_latest_parquet_file():
    """
    Define the function to find the latest parquet file
    """
    today = datetime.now().strftime('%Y-%m-%d')
    current_day_folder = os.path.join(PARQUET_PATH, today)
    
    for root, dirs, files in os.walk(current_day_folder):
        for file in files:
            if file.endswith('.parquet') and not file.startswith('[treated]'):
                return os.path.join(root, file)
    return None

def check_for_new_parquet_file(**context):
    """
    Define the PythonOperator to check for new parquet file
    """
    file_path = find_latest_parquet_file()
    if file_path:
        context['task_instance'].xcom_push(key='parquet_file_path', value=file_path)
    else:
        context['task_instance'].xcom_push(key='parquet_file_path', value=None)

def get_most_recent_file(directory):
    """
    Function to find the most recent file in a directory
    """
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def import_module_from_path(module_name, file_path):
    """
    Function to dynamically import a module
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module 

def process_parquet_file(**context):
    """
    Function to process the parquet file
    """
    file_path = context['task_instance'].xcom_pull(task_ids='check_for_new_parquet')
    if file_path:
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            df = pd.read_parquet(file_path)

            # Transform dataframe
            preprocessing_module = import_module_from_path('preprocessing_module', PROCESS_SCRIPT_PATH)
            df = preprocessing_module.preprocess_dataframe(df)
            
            # Check for the most recent macro table file
            most_recent_file = get_most_recent_file(MACRO_TABLE_PATH)
            consolidated_path = os.path.join(MACRO_TABLE_PATH, f"{today}.parquet")

            if most_recent_file:
                # If the most recent file is not named with today's date, create a copy with today's date
                if not most_recent_file.endswith(f"{today}.parquet"):
                    consolidated_path = os.path.join(MACRO_TABLE_PATH, f"{today}.parquet")
                    existing_df = pd.read_parquet(most_recent_file)
                    existing_df.to_parquet(consolidated_path, index=False)
                else:
                    consolidated_path = most_recent_file
            
            # Read the existing data if the file exists
            if os.path.exists(consolidated_path):
                existing_df = pd.read_parquet(consolidated_path)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            # Save the updated data to the consolidated path
            df.to_parquet(consolidated_path, index=False)
            print(f"Processed file: {file_path}")
            
            # Rename the file by prefixing with "[treated]"
            treated_path = os.path.join(os.path.dirname(file_path), f"[treated]_{os.path.basename(file_path)}")
            os.rename(file_path, treated_path)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            problematic_path = os.path.join(os.path.dirname(file_path), f"[problematic]_{os.path.basename(file_path)}")
            os.rename(file_path, problematic_path)
    else:
        print("No new parquet to process")

# DAG CONFIGURATION
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
    'FEED-WORKING-TABLE',
    default_args=default_args,
    description='A DAG to process new parquet files and then save historic version in a working table that will also be a .parquet file',
    schedule_interval=timedelta(seconds=5),
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
)

# PYTHON OPERATOR
# ---------------------------------------------------------------------------------
check_for_new_parquet = PythonOperator(
    task_id='check_for_new_parquet',
    python_callable=check_for_new_parquet_file,
    provide_context=True,
    dag=dag,
)
process_file = PythonOperator(
    task_id='process_file',
    python_callable=process_parquet_file,
    provide_context=True,
    dag=dag,
)

# ORCHESTRATION
# ---------------------------------------------------------------------------------
check_for_new_parquet >> process_file
