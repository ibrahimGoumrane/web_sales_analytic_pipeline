import unittest
from scraping.utils import handle_url

class TestScraperUtils(unittest.TestCase):
    def test_handle_url_adds_scheme(self):
        url = "www.jumia.ma/product"
        fixed = handle_url(url)
        self.assertTrue(fixed.startswith("https://"))
        self.assertIn("jumia.ma", fixed)

    def test_handle_url_keeps_https(self):
        url = "https://www.jumia.ma/product"
        fixed = handle_url(url)
        self.assertEqual(fixed, url)

if __name__ == "__main__":
    unittest.main()
