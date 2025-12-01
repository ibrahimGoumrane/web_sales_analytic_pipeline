"""
Main orchestrator for web scraping.
Handles scraper selection and execution.
"""

import logging
from typing import Optional

# Import all scrapers
from .jumia import Jumia
from .marjane import Marjane
from .avito import Avito
from .electroplanet import Electroplanet
from .bikhir import Bikhir
from .decathlon import Decathlon
from .hmizate import Hmizate

logger = logging.getLogger(__name__)


class ScraperOrchestrator:
    """
    Main class to orchestrate scraping across different websites.
    Uses Singleton pattern for scraper instances.
    """
    
    # Map of available scrapers
    SCRAPERS = {
        'jumia': Jumia,
        'marjane': Marjane,
        'avito': Avito,
        'electroplanet': Electroplanet,
        'bikhir': Bikhir,
        'decathlon': Decathlon,
        'hmizate': Hmizate,
    }
    
    @classmethod
    def run(cls, website: str, scrape_categories: bool = True, 
            scrape_products: bool = True, max_products: Optional[int] = 1000):
        """
        Run scraper for a specific website.
        
        Args:
            website: Name of the website to scrape ('jumia', 'marjane', etc.)
            scrape_categories: Whether to scrape categories
            scrape_products: Whether to scrape products
            max_products: Maximum products per category (None for unlimited)
            
        Returns:
            Scraper instance
            
        Raises:
            ValueError: If website is not supported
        """
        website = website.lower()
        
        if website not in cls.SCRAPERS:
            available = ', '.join(cls.SCRAPERS.keys())
            raise ValueError(
                f"Website '{website}' is not supported. "
                f"Available scrapers: {available}"
            )
        
        logger.info(f"🎯 Starting scraper for: {website}")
        
        # Get scraper class and instantiate (Singleton pattern ensures single instance)
        scraper_class = cls.SCRAPERS[website]
        scraper = scraper_class()
        
        # Run the scraper
        scraper.run(
            scrape_categories=scrape_categories,
            scrape_products=scrape_products,
            max_products=max_products
        )
        
        return scraper
    
    @classmethod
    def get_available_scrapers(cls):
        """Get list of available scraper names."""
        return list(cls.SCRAPERS.keys())
    
    @classmethod
    def is_scraper_available(cls, website: str):
        """Check if a scraper is available for a website."""
        return website.lower() in cls.SCRAPERS


# Convenience function for direct import
def run_scraper(website: str, **kwargs):
    """
    Convenience function to run a scraper.
    
    Args:
        website: Name of the website to scrape
        **kwargs: Additional arguments passed to ScraperOrchestrator.run()
        
    Returns:
        Scraper instance
    """
    return ScraperOrchestrator.run(website, **kwargs)


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Web Scraper Orchestrator')
    parser.add_argument('website', type=str, help='Website to scrape (jumia, marjane, etc.)')
    parser.add_argument('--no-categories', action='store_true', help='Skip category scraping')
    parser.add_argument('--no-products', action='store_true', help='Skip product scraping')
    parser.add_argument('--max-products', type=int, default=1000, help='Max products per category (0 for unlimited)')
    
    args = parser.parse_args()
    
    max_products = None if args.max_products == 0 else args.max_products
    
    run_scraper(
        website=args.website,
        scrape_categories=not args.no_categories,
        scrape_products=not args.no_products,
        max_products=max_products
    )
