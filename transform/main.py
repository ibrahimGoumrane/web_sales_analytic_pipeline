"""
Main orchestrator for web scraping.
Handles scraper selection and execution.
"""

import logging

# Import all cleaners
from .jumia import CleanDataJumia

logger = logging.getLogger(__name__)


class CleanDataOrchestrator:
    """
    Main class to orchestrate data cleaning across different websites.
    Currently supports Jumia only.
    """
    
    # Map of available cleaners
    CLEANERS = {
        'jumia': CleanDataJumia,
    }
    
    @classmethod
    def run(cls, website: str):
        """
        Run cleaner for a specific website.
        
        Args:
            website: Name of the website to clean ('jumia', 'marjane', etc.)
            
        Returns:
            Cleaner instance
            
        Raises:
            ValueError: If website is not supported
        """
        website = website.lower()
        
        if website not in cls.CLEANERS:
            available = ', '.join(cls.CLEANERS.keys())
            raise ValueError(
                f"Website '{website}' is not supported. "
                f"Available cleaners: {available}"
            )
        
        logger.info(f"🎯 Starting cleaner for: {website}")
        
        # Get cleaner class and instantiate (Singleton pattern ensures single instance)
        cleaner_class = cls.CLEANERS[website]
        cleaner = cleaner_class()
        
        # Run the cleaner
        cleaner.run()
        
        return cleaner
    
    @classmethod
    def get_available_cleaners(cls):
        """Get list of available cleaner names."""
        return list(cls.CLEANERS.keys())
    
    @classmethod
    def is_cleaner_available(cls, website: str):
        """Check if a cleaner is available for a website."""
        return website.lower() in cls.CLEANERS


# Convenience function for direct import
def run_cleaner(website: str, **kwargs):
    """
    Convenience function to run a cleaner.
    
    Args:
        website: Name of the website to clean
        **kwargs: Additional arguments passed to CleanDataOrchestrator.run()
        
    Returns:
        Cleaner instance
    """
    return CleanDataOrchestrator.run(website, **kwargs)


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Web Scraper Orchestrator')
    parser.add_argument('website', type=str, help='Website to clean (jumia, marjane, etc.)')
    
    args = parser.parse_args()

    run_cleaner(
        website=args.website,
    )
