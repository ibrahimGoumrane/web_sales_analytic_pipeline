#!/usr/bin/env python3
"""
Main entry point for generating sales analytics reports.
Usage: python main.py [website] [date]
Example: python main.py jumia 2025-12-01
"""

import sys
import logging
from datetime import datetime
from reports import generate_analytics_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the analytics report"""
    
    # Default values
    website = "jumia"
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        website = sys.argv[1]
    if len(sys.argv) > 2:
        date = sys.argv[2]
    
    logger.info(f"🚀 Starting analytics report generation")
    logger.info(f"   Website: {website}")
    logger.info(f"   Date: {date}")
    
    try:
        # Generate the report using the convenience function
        summary_text, summary_filename, _ = generate_analytics_report(website=website, date=date)
        
        # Print summary to console
        print("\n" + summary_text)
        
        logger.info("✅ Report generation completed successfully!")
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        logger.error("Please check that:")
        logger.error("  1. The website is valid (currently only 'jumia' is supported)")
        logger.error("  2. The date format is YYYY-MM-DD")
        logger.error("  3. Data exists for the specified date")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
