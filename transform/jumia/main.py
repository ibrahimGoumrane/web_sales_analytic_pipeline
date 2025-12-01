import pandas as pd
import os
import logging
from transform import CleanData

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

class CleanDataJumia(CleanData):
    """
    Jumia-specific data cleaning pipeline.
    """
    
    def __init__(self):
        """Initialize the Jumia data cleaner."""
        super().__init__('jumia')

    def clean(self, df):
        """
        Specific cleaning logic for Jumia data.
        """
        df = df.copy()
        
        # Clean prices
        if 'current_price' in df.columns:
            df['current_price'] = df['current_price'].apply(self._clean_price)
            
        if 'old_price' in df.columns:
            df['old_price'] = df['old_price'].apply(self._clean_price)
            
        # Clean discount (remove % and -)
        if 'discount' in df.columns:
            df['discount'] = df['discount'].astype(str).str.replace('%', '').str.replace('-', '').apply(self._clean_numeric)
            
        # Clean rating (already mostly numeric but good to ensure)
        if 'rating' in df.columns:
            df['rating'] = df['rating'].apply(self._clean_numeric)
            
        # Clean review count
        if 'review_count' in df.columns:
            df['review_count'] = df['review_count'].apply(self._clean_numeric)
            
        # Convert booleans
        bool_cols = ['is_official_store', 'has_express_delivery']
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(bool)
                
        # Handle dates
        if 'scraped_at' in df.columns:
            df['scraped_at'] = pd.to_datetime(df['scraped_at'])
            
        return df


if __name__ == "__main__":
    # Example usage
    cleaner = CleanDataJumia()
    cleaner.run()

