from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd
from scraping import run_scraper
from transform import run_cleaner
from load import PostgresLoader
import sys
"""
Allow Airflow to import modules from the project root
"""
sys.path.append('/opt/airflow/project')
os.chdir('/opt/airflow/project')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}

with DAG(
    'jumia_daily_etl',
    default_args=default_args,
    description='Daily ETL for Jumia: Scrape -> Transform -> Load',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    def scrape_jumia():
        """Scrape 1000 items per category from Jumia."""
        print("Starting Jumia scraping...")
        # Change to project directory so data is saved to mounted volume
        print(f"Working directory: {os.getcwd()}")
        run_scraper('jumia', max_products=100)
        print("Scraping completed.")

    def transform_jumia():
        """Clean the scraped Jumia data."""
        print("Starting Jumia transformation...")
        print(f"Working directory: {os.getcwd()}")
        run_cleaner('jumia')
        print("Transformation completed.")

    def load_jumia():
        """Load processed Jumia data into PostgreSQL."""
        print("Starting Jumia data loading...")
        # Path to processed data
        # Assuming code runs in project root or data is in /opt/airflow/project/data
        base_path = '/opt/airflow/project'
        processed_dir = os.path.join(base_path, 'data', 'processed', 'jumia')
        
        if not os.path.exists(processed_dir):
            print(f"No processed data found at {processed_dir}")
            return

        loader = PostgresLoader()
        # PostgresLoader connects in __init__
        
        try:
            files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
            print(f"Found {len(files)} files to load.")
            
            for file in files:
                file_path = os.path.join(processed_dir, file)
                print(f"Loading file: {file}")
                df = pd.read_csv(file_path)
                loader.load_data(df, 'jumia')
                print(f"Loaded {len(df)} rows from {file}")
                
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
        finally:
            loader.close()
            print("Database connection closed.")

    t1 = PythonOperator(
        task_id='scrape_jumia',
        python_callable=scrape_jumia,
    )

    t2 = PythonOperator(
        task_id='transform_jumia',
        python_callable=transform_jumia,
    )

    t3 = PythonOperator(
        task_id='load_jumia',
        python_callable=load_jumia,
    )

    t1 >> t2 >> t3
