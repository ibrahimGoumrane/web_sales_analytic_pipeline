import os
import logging
import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostgresLoader:
    """
    Handles loading of processed data into PostgreSQL.
    Automatically connects and initializes schema on instantiation.
    """
    
    def __init__(self):
        """Initialize database connection parameters and setup DB."""
        self.host = "localhost" # Assuming running from host
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.target_database = "sales_analytics" # New dedicated database
        self.default_database = os.getenv("POSTGRES_DB", "airflow") # Default DB to connect to initially
        self.user = os.getenv("POSTGRES_USER", "airflow")
        self.password = os.getenv("POSTGRES_PASSWORD", "airflow")
        self.conn = None
        
        # Initialize connection and schema immediately
        self._connect()
        self._init_schema()

    def _get_connection(self, db_name):
        """Helper to get a connection to a specific database."""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=db_name,
                user=self.user,
                password=self.password
            )
            return conn
        except Exception as e:
            logger.error(f"❌ Failed to connect to database '{db_name}': {e}")
            raise

    def _create_database(self):
        """Create the target database if it does not exist."""
        try:
            # Connect to default database to perform administrative tasks
            conn = self._get_connection(self.default_database)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            
            # Check if database exists
            cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.target_database}'")
            exists = cur.fetchone()
            
            if not exists:
                logger.info(f"🛠️ Database '{self.target_database}' not found. Creating...")
                cur.execute(f"CREATE DATABASE {self.target_database}")
                logger.info(f"✅ Database '{self.target_database}' created successfully")
            else:
                logger.info(f"ℹ️ Database '{self.target_database}' already exists")
                
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error checking/creating database: {e}")
            raise

    def _connect(self):
        """Establish connection to the target database."""
        self._create_database() # Ensure DB exists before connecting
        try:
            self.conn = self._get_connection(self.target_database)
            logger.info(f"✅ Connected to PostgreSQL database: {self.target_database}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to target database: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Connection closed")

    def _init_schema(self):
        """Initialize the database schema."""
        if not self.conn:
            self._connect()
            
        create_table_query = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            website VARCHAR(50) NOT NULL,
            sku VARCHAR(100), -- Stock Keeping Unit: Unique identifier for the product (e.g., 'SA024MP0ZDJYKNAFAMZ')
            name TEXT,
            url TEXT,
            current_price NUMERIC(10, 2),
            old_price NUMERIC(10, 2),
            discount NUMERIC(5, 2),
            rating NUMERIC(3, 2),
            review_count INTEGER,
            is_official_store BOOLEAN,
            image_url TEXT,
            scraped_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(website, sku, scraped_at)
        );
        
        CREATE INDEX IF NOT EXISTS idx_products_website ON products(website);
        CREATE INDEX IF NOT EXISTS idx_products_scraped_at ON products(scraped_at);
        """
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(create_table_query)
                self.conn.commit()
            logger.info("✅ Database schema initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize schema: {e}")
            self.conn.rollback()
            raise

    def load_data(self, df, website):
        """
        Load a pandas DataFrame into the products table.
        
        Args:
            df (pd.DataFrame): Processed data
            website (str): Website name
        """
        if not self.conn:
            self._connect()
            
        # Ensure columns match schema
        df['website'] = website
        
        # Select and order columns to match insert query
        columns = [
            'website', 'sku', 'name', 'url', 'current_price', 'old_price', 
            'discount', 'rating', 'review_count', 'is_official_store', 
            'image_url', 'scraped_at'
        ]
        
        # Handle missing columns by adding them as None
        for col in columns:
            if col not in df.columns:
                df[col] = None
                
        # Replace NaN with None for SQL compatibility
        df = df.where(pd.notnull(df), None)
        
        data_tuples = [tuple(x) for x in df[columns].to_numpy()]
        
        insert_query = """
        INSERT INTO products (
            website, sku, name, url, current_price, old_price, 
            discount, rating, review_count, is_official_store, 
            image_url, scraped_at
        ) VALUES %s
        ON CONFLICT (website, sku, scraped_at) DO NOTHING
        """
        
        try:
            with self.conn.cursor() as cur:
                execute_values(cur, insert_query, data_tuples)
                self.conn.commit()
            logger.info(f"✅ Loaded {len(df)} rows for {website}")
        except Exception as e:
            logger.error(f"❌ Failed to load data: {e}")
            self.conn.rollback()
            raise

if __name__ == "__main__":
    # Example usage
    loader = PostgresLoader()
    try:
        # Connection and schema init happen automatically on instantiation
        pass 
    finally:
        loader.close()
