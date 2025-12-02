from airflow import DAG
from airflow.sdk import task
from datetime import datetime, timedelta
import os
import pandas as pd
from scraping import run_scraper
from transform import run_cleaner
from load import PostgresLoader
import sys
# NOTE: Do not import `generate_analytics_report` at module import time.
# Importing the reports package may require optional plotting libraries
# (matplotlib/seaborn). To keep the DAG import-safe, the report function
# is imported lazily inside the task function below.
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
    start_date=datetime(2025, 12, 2),
    catchup=False,
) as dag:

    @task(task_id="scrape_jumia")
    def scrape_jumia():
        """Scrape 1000 items per category from Jumia."""
        print("Starting Jumia scraping...")
        # Change to project directory so data is saved to mounted volume
        print(f"Working directory: {os.getcwd()}")
        run_scraper('jumia', max_products=100)
        print("Scraping completed.")

    @task(task_id="transform_jumia")
    def transform_jumia():
        """Clean the scraped Jumia data."""
        print("Starting Jumia transformation...")
        print(f"Working directory: {os.getcwd()}")
        run_cleaner('jumia')
        print("Transformation completed.")

    @task(task_id="load_jumia")
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

    # Set up task dependencies
    scrape_jumia() >> transform_jumia() >> load_jumia()


with DAG(
    'analytics_report_param',
    default_args=default_args,
    description='Generate analytics report for a given website and date',
    schedule=None,  # Only manual or API-triggered
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    @task(task_id="generate_report")
    def generate_report(**context):
        """Generate analytics report with optional parameters."""
        # Read parameters passed when triggering the DAG
        conf = context.get('dag_run').conf or {}
        website = conf.get('website', 'jumia')   # default to jumia
        date = conf.get('date')                  # expects 'YYYY-MM-DD' or None

        print(f"Generating report for website={website}, date={date}")
        # Import the report generator here to avoid requiring plotting
        # dependencies during DAG parsing.
        from reports import generate_analytics_report
        generate_analytics_report(website=website, date=date)

    # Execute the task
    generate_report()
