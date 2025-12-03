import unittest
import pandas as pd
from load.load_postgres import PostgresLoader

class TestLoader(unittest.TestCase):
    def test_schema_and_idempotent_insert(self):
        loader = PostgresLoader()
        try:
            df = pd.DataFrame({
                'sku': ['SKU123'],
                'name': ['Test Product'],
                'category': ['TestCat'],
                'url': ['https://www.jumia.ma/test'],
                'current_price': [199.99],
                'old_price': [249.99],
                'discount': [20.0],
                'rating': [4.5],
                'review_count': [10],
                'is_official_store': [True],
                'image_url': ['https://example.com/img.png'],
                'scraped_at': [pd.Timestamp.utcnow()]
            })
            loader.load_data(df, 'jumia')
            # Load same data again to verify ON CONFLICT DO NOTHING
            loader.load_data(df, 'jumia')
        finally:
            loader.close()

if __name__ == "__main__":
    unittest.main()
