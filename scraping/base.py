from abc import ABC, abstractmethod
import requests
import json
import csv
import os
import time
import logging

logger = logging.getLogger(__name__)


class Base(ABC):
    """
    Abstract base class for scraping e-commerce sites.
    Provides common functionality for HTTP requests, data storage, and session management.
    Cannot be instantiated directly - must be subclassed.
    """
    
    # Class-level constants
    sites_available = ["jumia", "marjane", "electroplanet", "bikhir", "decathlon", "hmizate"]
    
    def __init__(self, site_name, base_url):
        """
        Initialize the base scraper.
        
        Args:
            site_name: Name of the site (e.g., 'jumia')
            base_url: Base URL of the site (e.g., 'https://www.jumia.ma')
        """
        if site_name not in self.sites_available:
            raise ValueError(f"Site {site_name} is not available. Choose from: {self.sites_available}")
        
        self.site = site_name
        self.base_url = base_url
        self.categories = []
        self.products = []
        
        # Create data directories
        self.data_dir = os.path.join("data", "raw", site_name)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create logs directory
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Initialize HTTP session with browser-like headers
        self.session = self._init_session()
    
    def _init_session(self):
        """
        Initialize requests session with browser-like headers.
        
        Returns:
            requests.Session object
        """
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        return session
    
    def _make_request(self, url, max_retries=3, timeout=15, delay=1):
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 15)
            delay: Delay between requests in seconds (default: 1)
            
        Returns:
            Response object or None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching: {url} (Attempt {attempt + 1}/{max_retries})")
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                
                # Polite delay to avoid overwhelming the server
                time.sleep(delay)
                
                return response
                
            except requests.exceptions.HTTPError as e:
                logger.warning(f"HTTP Error {e.response.status_code}: {e}")
                if e.response.status_code == 404:
                    logger.error(f"Page not found: {url}")
                    return None
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error: {e}")
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"Request timeout: {e}")
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed: {e}")
            
            # Exponential backoff for retries
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed after {max_retries} attempts: {url}")
                return None
    
    def _save_json(self, data, filename):
        """
        Save data to JSON file.
        
        Args:
            data: Data to save (list or dict)
            filename: Output filename
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Saved {len(data) if isinstance(data, list) else 'data'} to {filepath}")
        except Exception as e:
            logger.error(f"❌ Error saving JSON to {filename}: {e}")
    
    def _save_csv(self, data, filename):
        """
        Save data to CSV file.
        
        Args:
            data: List of dictionaries to save
            filename: Output filename
        """
        try:
            if not data:
                logger.warning("⚠️ No data to save to CSV")
                return
            
            filepath = os.path.join(self.data_dir, filename)
            
            # Get all unique keys from all dictionaries
            fieldnames = set()
            for item in data:
                if isinstance(item, dict):
                    fieldnames.update(item.keys())
            
            if not fieldnames:
                logger.warning("⚠️ No valid data structure for CSV export")
                return
            
            fieldnames = sorted(fieldnames)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"✅ Saved {len(data)} rows to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error saving CSV to {filename}: {e}")
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
            logger.info("🔒 HTTP session closed")
    
    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def scrape_categories(self):
        """Scrape the main categories of the website."""
        pass

    @abstractmethod
    def scrape_product_list(self, category_url, max_products=1000):
        """
        Scrape product listings from a category page.
        
        Args:
            category_url: URL of the category page
            max_products: Maximum number of products to scrape (default: 1000, use None for unlimited)
        """
        pass

    @abstractmethod
    def run(self, **kwargs):
        """
        Run the complete scraping workflow.
        Implementation should handle the full scraping process.
        """
        pass
