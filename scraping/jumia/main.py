from bs4 import BeautifulSoup
from datetime import datetime
import logging
import os
import re
from scraping import Base , handle_url

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "jumia.log")),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)


class Jumia(Base):
    """
    Jumia.ma web scraper for extracting product data.
    Inherits common functionality from Main base class.
    Uses BeautifulSoup for static content scraping.
    """
    
    def __init__(self):
        """Initialize Jumia scraper."""
        # Call parent constructor
        super().__init__(site_name="jumia", base_url="https://www.jumia.ma")
        logger.info("🚀 Jumia scraper initialized")
    
    def scrape_categories(self):
        """
        Scrape main product categories from Jumia homepage.
        Extracts category name and URL.
        """
        logger.info("📂 Starting category scraping...")
        
        try:
            response = self._make_request(self.base_url)
            if not response:
                logger.error("❌ Failed to fetch homepage")
                return
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find category links - targeting menu items
            category_links = soup.find_all('a', href=True, role="menuitem")
            
            if not category_links:
                logger.warning("⚠️ No category links with role='menuitem' found, trying alternative selectors...")
                # Fallback: try other common category selectors
                category_links = soup.select('nav a[href*="/"]')
            
            seen_categories = set()
            
            for link in category_links:
                try:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Filter for main category pages
                    if (href and text and 
                        not href.startswith('#') and 
                        len(text) > 2 and
                        href not in seen_categories):
                        
                        # Build full URL using utility function
                        full_url = handle_url(href, self.base_url)
                        if not full_url or href.startswith('http') and not href.startswith(self.base_url):
                            continue
                        
                        category_data = {
                            'name': text,
                            'url': full_url,
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        self.categories.append(category_data)
                        seen_categories.add(href)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error processing category link: {e}")
                    continue
            
            logger.info(f"✅ Found {len(self.categories)} categories")
            
            # Save to CSV in categories directory
            if self.categories:
                self._save_csv(self.categories, f"{self.site}.csv", is_category=True)
            else:
                logger.warning("⚠️ No categories found to save")
            
        except Exception as e:
            logger.error(f"❌ Error in scrape_categories: {e}")
    
    def scrape_product_list(self, category_url, max_products=1000):
        """
        Scrape product listings from a category page by following the Next button.
        
        Args:
            category_url: URL of the category page to start from
            max_products: Maximum number of products to scrape (default: 1000, use None for unlimited)
        """
        logger.info(f"📦 Scraping product list: {category_url}")
        logger.info(f"🎯 Target: {max_products if max_products else 'All available'} products")
        
        current_url = category_url
        page_num = 1
        initial_count = len(self.products)
        
        while True:
            try:
                # Check if we've reached the product limit
                if max_products and (len(self.products) - initial_count) >= max_products:
                    logger.info(f"🎯 Reached target of {max_products} products")
                    break
                
                # Fetch the current page
                response = self._make_request(current_url)
                if not response:
                    logger.warning(f"⚠️ Failed to fetch page {page_num}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product articles
                products = soup.select('article.prd._fb.col.c-prd')
                
                if not products:
                    logger.info(f"🛑 No products found on page {page_num}, stopping")
                    break
                
                logger.info(f"  📄 Page {page_num}: Found {len(products)} products")
                
                # Extract product data
                products_added = 0
                for product in products:
                    # Check product limit before adding each product
                    if max_products and (len(self.products) - initial_count) >= max_products:
                        break
                        
                    product_data = self._extract_product_data(product)
                    if product_data:
                        self.products.append(product_data)
                        products_added += 1
                        
                        # Incremental save every 100 products
                        if len(self.products) % 100 == 0:
                            from datetime import datetime
                            filename = f"jumia_products_{datetime.now().strftime('%Y%m%d')}.csv"
                            self._save_csv(self.products, filename)
                
                logger.info(f"  ✅ Added {products_added} products (Total: {len(self.products) - initial_count})")
                
                # Check if we've reached the limit
                if max_products and (len(self.products) - initial_count) >= max_products:
                    logger.info(f"🎯 Reached target of {max_products} products")
                    break
                
                # Find the "Next" button and get its URL
                next_button = soup.select_one('a.pg[aria-label*="suivante"]')
                
                if not next_button:
                    logger.info("🏁 No 'Next' button found - reached the last page")
                    break
                
                next_href = next_button.get('href')
                if not next_href:
                    logger.info("🏁 'Next' button has no href - reached the last page")
                    break
                
                # Build the next URL using utility function
                current_url = handle_url(next_href, self.base_url)
                
                page_num += 1
                logger.info(f"  ➡️ Following Next button to page {page_num}")
                    
            except Exception as e:
                logger.error(f"❌ Error scraping page {page_num}: {e}")
                break
        
        products_scraped = len(self.products) - initial_count
        logger.info(f"✅ Scraped {products_scraped} products from this category ({page_num} pages)")
        logger.info(f"📊 Total products in memory: {len(self.products)}")
        
        # Final save to ensure all products are persisted
        if self.products:
            from datetime import datetime
            filename = f"jumia_products_{datetime.now().strftime('%Y%m%d')}.csv"
            self._save_csv(self.products, filename)
    
    def _extract_product_data(self, product_element):
        """
        Extract product data from a product card element.
        
        Args:
            product_element: BeautifulSoup element containing product info
            
        Returns:
            Dictionary with product data or None if extraction fails
        """
        try:
            data = {}
            
            # Product name
            name_elem = product_element.select_one('h3.name')
            data['name'] = name_elem.get_text(strip=True) if name_elem else None
            
            # Current price
            price_elem = product_element.select_one('div.prc')
            data['current_price'] = price_elem.get_text(strip=True) if price_elem else None
            
            # Old price (if on sale)
            old_price_elem = product_element.select_one('div.old')
            data['old_price'] = old_price_elem.get_text(strip=True) if old_price_elem else None
            
            # Discount percentage
            discount_elem = product_element.select_one('div.bdg._dsct')
            data['discount'] = discount_elem.get_text(strip=True) if discount_elem else None
            
            # Rating
            rating_elem = product_element.select_one('div.stars._s')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                # Extract numeric rating (e.g., "4.4 out of 5")
                data['rating'] = rating_text.split()[0] if rating_text else None
            else:
                data['rating'] = None
            
            # Review count
            review_elem = product_element.select_one('div.rev')
            if review_elem:
                review_text = review_elem.get_text(strip=True)
                # Extract number from parentheses
                match = re.search(r'\((\d+)\)', review_text)
                data['review_count'] = match.group(1) if match else None
            else:
                data['review_count'] = None
            
            # Product URL
            link_elem = product_element.select_one('a.core')
            if link_elem:
                href = link_elem.get('href', '')
                data['url'] = handle_url(href, self.base_url)
            else:
                data['url'] = None
            
            # Image URL
            img_elem = product_element.select_one('img.img')
            data['image_url'] = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
            
            # Brand (from data attributes)
            data['brand'] = link_elem.get('data-ga4-item_brand') if link_elem else None
            
            # SKU
            data['sku'] = link_elem.get('data-sku') if link_elem else None
            
            # Category hierarchy
            if link_elem:
                data['category'] = link_elem.get('data-ga4-item_category')
                data['category_2'] = link_elem.get('data-ga4-item_category2')
                data['category_3'] = link_elem.get('data-ga4-item_category3')
            
            # Official store badge
            mall_badge = product_element.select_one('div.bdg._mall')
            data['is_official_store'] = bool(mall_badge)
            
            
            # Scrape metadata
            data['scraped_at'] = datetime.now().isoformat()
            data['source'] = 'jumia.ma'
            
            return data
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting product data: {e}")
            return None
    
    def scrape_all_categories(self, max_products_per_category=1000):
        """
        Scrape products from all discovered categories.
        
        Args:
            max_products_per_category: Maximum products to scrape per category (default: 1000, use None for unlimited)
        """
        if not self.categories:
            logger.warning("⚠️ No categories found. Run scrape_categories() first.")
            return
        
        logger.info(f"🔄 Scraping {len(self.categories)} categories...")
        
        for idx, category in enumerate(self.categories, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"📂 [{idx}/{len(self.categories)}] Processing: {category['name']}")
            logger.info(f"{'='*60}")
            
            try:
                self.scrape_product_list(
                    category['url'], 
                    max_products=max_products_per_category
                )
            except Exception as e:
                logger.error(f"❌ Failed to scrape category {category['name']}: {e}")
                continue
        
    
    def run(self, scrape_categories=True, scrape_products=True, max_products=1000):
        """
        Run the complete scraping workflow.
        
        Args:
            scrape_categories: Whether to scrape categories
            scrape_products: Whether to scrape product listings
            max_products: Maximum products per category (default: 1000, use None for unlimited)
        """
        logger.info("=" * 60)
        logger.info("🚀 Starting Jumia.ma Scraper")
        logger.info("=" * 60)
        
        try:
            if scrape_categories:
                self.scrape_categories()
            
            if scrape_products:
                if self.categories:
                    self.scrape_all_categories(max_products_per_category=max_products)
                else:
                    logger.warning("⚠️ No categories to scrape products from")
            
            logger.info("\n" + "=" * 60)
            logger.info("✨ Scraping completed successfully!")
            logger.info(f"📊 Categories: {len(self.categories)}")
            logger.info(f"📦 Products: {len(self.products)}")
            logger.info(f"💾 Data saved to: {self.data_dir}")
            logger.info("=" * 60)
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️ Scraping interrupted by user")
            # Save partial data
            if self.products:
                logger.info("💾 Saving partial data...")
                self._save_json(self.products, 'products_partial.json')
                self._save_csv(self.products, 'products_partial.csv')
        except Exception as e:
            logger.error(f"❌ Fatal error in run(): {e}", exc_info=True)
        finally:
            self.close()


# Example usage
if __name__ == "__main__":
    scraper = Jumia()
    
    # Option 1: Full workflow with product limit
    scraper.run(scrape_categories=True, scrape_products=True, max_products=500)
    
    # Option 2: Unlimited scraping (scrape all products)
    # scraper.run(scrape_categories=True, scrape_products=True, max_products=None)
    
    # Option 3: Step by step
    # scraper.scrape_categories()
    # scraper.scrape_product_list("https://www.jumia.ma/telephone-tablette/", max_products=1000)


    """
    Jumia.ma web scraper for extracting product data.
    Uses BeautifulSoup for static content scraping.
    """
    
    def __init__(self):
        self.site = "jumia"
        self.base_url = "https://www.jumia.ma"
        self.categories = []
        self.products = []
        
        # Create data directories
        self.data_dir = os.path.join("data", "raw", "jumia")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Request headers to mimic browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, url, max_retries=3):
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response object or None if failed
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching: {url} (Attempt {attempt + 1}/{max_retries})")
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                time.sleep(1)  # Polite delay
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {max_retries} attempts: {url}")
                    return None
    
    def scrape_categories(self):
        """
        Scrape main product categories from Jumia homepage.
        Extracts category name and URL.
        """
        logger.info("Starting category scraping...")
        
        try:
            response = self._make_request(self.base_url)
            if not response:
                logger.error("Failed to fetch homepage")
                return
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find category links (adjust selector based on actual HTML)
            # Common patterns: nav links, category menu items
            category_links = soup.find_all('a', href=True, role="menuitem")
            
            seen_categories = set()
            
            for link in category_links:
                try:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Filter for main category pages
                    if (href and text and 
                        not href.startswith('#') and 
                        len(text) > 2 and
                        href not in seen_categories):
                        
                        # Build full URL
                        if href.startswith('/'):
                            full_url = self.base_url + href
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                        
                        category_data = {
                            'name': text,
                            'url': full_url,
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        self.categories.append(category_data)
                        seen_categories.add(href)
                        
                except Exception as e:
                    logger.warning(f"Error processing category link: {e}")
                    continue
            
            logger.info(f"Found {len(self.categories)} categories")
            
            # Save to JSON
            self._save_json(self.categories, 'categories.json')
            
        except Exception as e:
            logger.error(f"Error in scrape_categories: {e}")
    
    def scrape_product_list(self, category_url, max_pages=5):
        """
        Scrape product listings from a category page.
        
        Args:
            category_url: URL of the category page
            max_pages: Maximum number of pages to scrape
        """
        logger.info(f"Scraping product list: {category_url}")
        
        for page in range(1, max_pages + 1):
            try:
                # Build pagination URL
                if '?' in category_url:
                    page_url = f"{category_url}&page={page}"
                else:
                    page_url = f"{category_url}?page={page}"
                
                response = self._make_request(page_url)
                if not response:
                    logger.warning(f"Failed to fetch page {page}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product articles
                products = soup.select('article.prd')
                
                if not products:
                    logger.info(f"No products found on page {page}, stopping pagination")
                    break
                
                logger.info(f"Found {len(products)} products on page {page}")
                
                for product in products:
                    product_data = self._extract_product_data(product)
                    if product_data:
                        self.products.append(product_data)
                
                # Check if there's a next page
                next_page = soup.select_one('a.pg[aria-label*="suivante"]')
                if not next_page:
                    logger.info("No more pages available")
                    break
                    
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                continue
        
        logger.info(f"Total products scraped: {len(self.products)}")
    
    def _extract_product_data(self, product_element):
        """
        Extract product data from a product card element.
        
        Args:
            product_element: BeautifulSoup element containing product info
            
        Returns:
            Dictionary with product data or None if extraction fails
        """
        try:
            data = {}
            
            # Product name
            name_elem = product_element.select_one('h3.name')
            data['name'] = name_elem.get_text(strip=True) if name_elem else None
            
            # Current price
            price_elem = product_element.select_one('div.prc')
            data['current_price'] = price_elem.get_text(strip=True) if price_elem else None
            
            # Old price (if on sale)
            old_price_elem = product_element.select_one('div.old')
            data['old_price'] = old_price_elem.get_text(strip=True) if old_price_elem else None
            
            # Discount percentage
            discount_elem = product_element.select_one('div.bdg._dsct')
            data['discount'] = discount_elem.get_text(strip=True) if discount_elem else None
            
            # Rating
            rating_elem = product_element.select_one('div.stars._s')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                # Extract numeric rating (e.g., "4.4 out of 5")
                data['rating'] = rating_text.split()[0] if rating_text else None
            else:
                data['rating'] = None
            
            # Review count
            review_elem = product_element.select_one('div.rev')
            if review_elem:
                review_text = review_elem.get_text(strip=True)
                # Extract number from parentheses
                import re
                match = re.search(r'\((\d+)\)', review_text)
                data['review_count'] = match.group(1) if match else None
            else:
                data['review_count'] = None
            
            # Product URL
            link_elem = product_element.select_one('a.core')
            if link_elem:
                href = link_elem.get('href', '')
                data['url'] = self.base_url + href if href.startswith('/') else href
            else:
                data['url'] = None
            
            # Image URL
            img_elem = product_element.select_one('img.img')
            data['image_url'] = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
            
            # Brand (from data attributes)
            link_elem = product_element.select_one('a.core')
            data['brand'] = link_elem.get('data-ga4-item_brand') if link_elem else None
            
            # SKU
            data['sku'] = link_elem.get('data-sku') if link_elem else None
            
            # Category
            if link_elem:
                data['category'] = link_elem.get('data-ga4-item_category')
                data['category_2'] = link_elem.get('data-ga4-item_category2')
                data['category_3'] = link_elem.get('data-ga4-item_category3')
            
            # Official store badge
            mall_badge = product_element.select_one('div.bdg._mall')
            data['is_official_store'] = bool(mall_badge)
            
            
            # Scrape metadata
            data['scraped_at'] = datetime.now().isoformat()
            data['source'] = 'jumia.ma'
            
            return data
            
        except Exception as e:
            logger.warning(f"Error extracting product data: {e}")
            return None
    
    def scrape_all_categories(self, max_pages_per_category=3):
        """
        Scrape products from all discovered categories.
        
        Args:
            max_pages_per_category: Max pages to scrape per category
        """
        if not self.categories:
            logger.warning("No categories found. Run scrape_categories() first.")
            return
        
        logger.info(f"Scraping {len(self.categories)} categories...")
        
        for idx, category in enumerate(self.categories, 1):
            logger.info(f"[{idx}/{len(self.categories)}] Processing: {category['name']}")
            
            try:
                self.scrape_product_list(
                    category['url'], 
                    max_pages=max_pages_per_category
                )
            except Exception as e:
                logger.error(f"Failed to scrape category {category['name']}: {e}")
                continue
        
        # Save all products
        self._save_json(self.products, 'products.json')
        self._save_csv(self.products, 'products.csv')
    
    def _save_json(self, data, filename):
        """Save data to JSON file."""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(data)} items to {filepath}")
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")
    
    def _save_csv(self, data, filename):
        """Save data to CSV file."""
        try:
            if not data:
                logger.warning("No data to save to CSV")
                return
            
            filepath = os.path.join(self.data_dir, filename)
            
            # Get all unique keys
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(fieldnames)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Saved {len(data)} items to {filepath}")
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
    
    def run(self, scrape_categories=True, scrape_products=True, max_pages=3):
        """
        Run the complete scraping workflow.
        
        Args:
            scrape_categories: Whether to scrape categories
            scrape_products: Whether to scrape product listings
            max_pages: Maximum pages per category
        """
        logger.info("=" * 60)
        logger.info("Starting Jumia.ma Scraper")
        logger.info("=" * 60)
        
        try:
            if scrape_categories:
                self.scrape_categories()
            
            if scrape_products:
                if self.categories:
                    self.scrape_all_categories(max_pages_per_category=max_pages)
                else:
                    logger.warning("No categories to scrape products from")
            
            logger.info("=" * 60)
            logger.info("Scraping completed successfully!")
            logger.info(f"Categories: {len(self.categories)}")
            logger.info(f"Products: {len(self.products)}")
            logger.info(f"Data saved to: {self.data_dir}")
            logger.info("=" * 60)
            
        except KeyboardInterrupt:
            logger.warning("Scraping interrupted by user")
            # Save partial data
            if self.products:
                self._save_json(self.products, 'products_partial.json')
                self._save_csv(self.products, 'products_partial.csv')
        except Exception as e:
            logger.error(f"Fatal error in run(): {e}")
        finally:
            self.session.close()


# Example usage
if __name__ == "__main__":
    scraper = Jumia()
    
    # Option 1: Full workflow
    scraper.run(scrape_categories=True, scrape_products=True, max_products=1000)
    

