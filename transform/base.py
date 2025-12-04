from abc import ABC, abstractmethod
import pandas as pd
import os
import logging
import re
from datetime import datetime

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "transform.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CleanData(ABC):
    """
    Abstract base class for data cleaning and transformation pipelines.
    Reads raw data from data/raw/{website}, cleans it, and saves to data/processed/{website}.
    """
    
    def __init__(self, website_name):
        """
        Initialize the data cleaner.
        
        Args:
            website_name (str): The name of the website (e.g., 'jumia', 'marjane').
        """
        self.website_name = website_name
        self.raw_dir = os.path.join("data", "raw")
        self.processed_dir = os.path.join("data", "processed")
        
        # Ensure directories exist
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def _clean_price(self, price_str):
        """
        Clean price string to float.
        Example: '1,229.00 Dhs' -> 1229.00
        """
        if pd.isna(price_str):
            return None
        try:
            # Convert to string
            s = str(price_str)
            # Remove currency symbols (DH, Dhs, etc.) and whitespace
            # Keep digits, dots, commas
            s = re.sub(r'[^\d.,]', '', s)
            
            if not s:
                return None

            # Handle comma as decimal if it appears at the end like 299,99
            # But handle 1,229.00 (comma is thousands)
            
            if ',' in s and '.' in s:
                if s.find(',') < s.find('.'):
                    s = s.replace(',', '') # 1,234.56 -> 1234.56
                else:
                    s = s.replace('.', '').replace(',', '.') # 1.234,56 -> 1234.56
            elif ',' in s:
                s = s.replace(',', '.')
            
            return float(s)
        except (ValueError, TypeError):
            return None

    def _clean_numeric(self, value):
        """Extract numeric value from string."""
        if pd.isna(value):
            return None
        try:
            if isinstance(value, (int, float)):
                return float(value)
            
            s = str(value).strip()
            # Handle comma decimal
            s = s.replace(',', '.')
            
            # Extract first number found
            match = re.search(r'(\d+(\.\d+)?)', s)
            return float(match.group(1)) if match else None
        except Exception:
            return None

    @abstractmethod
    def clean(self, df):
        """
        Apply website-specific cleaning logic.
        
        Args:
            df (pd.DataFrame): Raw data.
            
        Returns:
            pd.DataFrame: Cleaned data.
        """
        pass

    def save(self, data, path):
        """Save processed data to CSV."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data.to_csv(path, index=False)
            logger.info(f"💾 Saved processed data to {path}")
        except Exception as e:
            logger.error(f"❌ Error saving data to {path}: {e}")

    def run(self):
        """
        Process all files for the specific website.
        """
        try:
            website = self.website_name
            
            website_raw_dir = os.path.join(self.raw_dir, website)
            website_processed_dir = os.path.join(self.processed_dir, website)
            
            if not os.path.exists(website_raw_dir):
                logger.warning(f"⚠️ No raw data folder found for {website}")
                return False
            
            files = [f for f in os.listdir(website_raw_dir) if f.endswith('.csv')]
            
            if not files:
                logger.warning(f"⚠️ No CSV files found in {website_raw_dir}")
                return False
            
            logger.info(f"🔄 Processing {len(files)} files for {website}...")
            
            for file in files:
                raw_path = os.path.join(website_raw_dir, file)
                processed_path = os.path.join(website_processed_dir, file)
                
                try:
                    # Read raw data
                    df = pd.read_csv(raw_path)
                    
                    # Clean data
                    cleaned_df = self.clean(df)
                    
                    # Save processed data
                    self.save(cleaned_df, processed_path)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing file {file}: {e}")
                    continue
            
            logger.info(f"✅ Completed processing for {website}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in run for {self.website_name}: {e}")
            return False

if __name__ == "__main__":
    # Example usage (CleanData is now an abstract class and cannot be instantiated directly)
    # You would create a concrete class like this:
    # class JumiaCleaner(CleanData):
    #     def __init__(self):
    #         super().__init__('jumia')
    #     def clean(self, df):
    #         # Implement Jumia-specific cleaning here
    #         logger.info("Cleaning Jumia data...")
    #         return df # Placeholder
    #
    # jumia_cleaner = JumiaCleaner()
    # jumia_cleaner.run()
    pass

