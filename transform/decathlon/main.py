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

class CleanDataDecathlon(CleanData):
    """
    Decathlon-specific data cleaning pipeline.
    """
    
    def __init__(self):
        """Initialize the Decathlon data cleaner."""
        super().__init__('decathlon')

    def clean(self, df):
        """
        Specific cleaning logic for Decathlon data.
        """
        df = df.copy()
        # Add specific cleaning logic here
        return df

if __name__ == "__main__":
    cleaner = CleanDataDecathlon()
    cleaner.run()
