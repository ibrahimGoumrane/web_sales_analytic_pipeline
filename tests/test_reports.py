import unittest
import os
from reports import generate_analytics_report

class TestReports(unittest.TestCase):
    def test_generate_reports_creates_outputs(self):
        # Use today's date; assumes ETL loaded data for jumia today
        summary_text, summary_file = generate_analytics_report(website="jumia")
        # Check that a reports directory exists
        base_dir = os.path.join('data', 'reports')
        self.assertTrue(os.path.isdir(base_dir))

if __name__ == "__main__":
    unittest.main()
