import unittest
import pandas as pd
from transform.jumia.main import CleanDataJumia

class TestTransformer(unittest.TestCase):
    def test_price_cleaning(self):
        df = pd.DataFrame({
            'current_price': ['299,99 DH', '1 249.00 DH', None],
            'old_price': ['399 DH', None, '0 DH'],
            'discount': ['25%', '10 %', None],
            'rating': ['4.5', '3,9', None],
            'review_count': ['120', '0', None],
            'is_official_store': ['Official Store', 'Non-Official Store', None],
        })
        cleaner = CleanDataJumia()
        out = cleaner.clean(df)
        print(out['current_price'].dtype.kind)
        self.assertTrue(out['current_price'].dtype.kind in 'fi')
        self.assertTrue(out['old_price'].dtype.kind in 'fi')
        self.assertTrue(out['discount'].dtype.kind in 'fi')
        self.assertTrue(out['rating'].dtype.kind in 'fi')
        self.assertTrue(out['review_count'].dtype.kind in 'fi')
        self.assertIn('is_official_store', out.columns)

if __name__ == "__main__":
    unittest.main()
