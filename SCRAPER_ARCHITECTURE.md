# Scraper Architecture

## 📁 Project Structure

```
web_sales_analytic_pipeline/
├── scraping/
│   ├── __init__.py              # Package exports
│   ├── main.py                  # Base class (Main) with shared functionality
│   └── jumia/
│       ├── __init__.py          # Jumia package exports
│       └── main.py              # Jumia scraper (inherits from Main)
├── data/
│   └── raw/
│       └── jumia/               # Scraped data stored here
├── logs/
│   └── jumia.log                # Scraping logs
└── test_scraper.py              # Test script
```

## 🏗️ Architecture Overview

### **Base Class: `Main`** (`scraping/main.py`)

**Shared functionality across all scrapers:**

- ✅ HTTP session management with browser headers
- ✅ Request retry logic with exponential backoff
- ✅ JSON/CSV data saving methods
- ✅ Directory creation (data & logs)
- ✅ Session cleanup
- ✅ Error handling patterns

**Abstract methods (must be implemented by child classes):**

- `scrape_categories()` - Scrape site categories
- `scrape_product_list(category_url, max_pages)` - Scrape products
- `run(**kwargs)` - Main workflow execution

### **Jumia Scraper** (`scraping/jumia/main.py`)

**Inherits from `Main` and implements:**

- ✅ Jumia-specific category scraping
- ✅ Product list pagination
- ✅ Product data extraction (name, price, rating, etc.)
- ✅ BeautifulSoup parsing logic
- ✅ Jumia HTML structure handling

## 🎯 Key Benefits

### **1. DRY Principle (Don't Repeat Yourself)**

- Common HTTP logic in parent class
- Shared data saving methods
- Consistent error handling

### **2. Easy to Extend**

Adding a new scraper (e.g., Avito, Marjane):

```python
from scraping.main import Main

class Avito(Main):
    def __init__(self):
        super().__init__(site_name="avito", base_url="https://www.avito.ma")

    def scrape_categories(self):
        # Avito-specific implementation
        pass

    def scrape_product_list(self, category_url, max_pages=5):
        # Avito-specific implementation
        pass

    def run(self, **kwargs):
        # Avito workflow
        pass
```

### **3. Centralized Updates**

- Update retry logic once → affects all scrapers
- Improve logging once → benefits all scrapers
- Add new save formats (Excel, Parquet) → available everywhere

## 📊 Data Flow

```
1. Initialize Scraper
   └─> Main.__init__() creates session, directories

2. Scrape Categories
   └─> Jumia.scrape_categories()
       └─> Main._make_request() gets HTML
       └─> BeautifulSoup parses
       └─> Main._save_json() saves results

3. Scrape Products
   └─> Jumia.scrape_product_list()
       └─> Main._make_request() for each page
       └─> Extract data
       └─> Accumulate in self.products

4. Save Results
   └─> Main._save_json() & Main._save_csv()

5. Cleanup
   └─> Main.close() closes session
```

## 🚀 Usage Examples

### Quick Test

```bash
python test_scraper.py
```

### Full Scraping

```python
from scraping.jumia import Jumia

scraper = Jumia()
scraper.run(scrape_categories=True, scrape_products=True, max_pages=3)
```

### Custom Workflow

```python
from scraping.jumia import Jumia

scraper = Jumia()
scraper.scrape_categories()
scraper.scrape_product_list("https://www.jumia.ma/telephone-tablette/", max_pages=5)
scraper.close()
```

## 🔧 Configuration

### Logging

- **Console output**: Real-time progress
- **File output**: `logs/jumia.log`
- **Format**: `timestamp - level - message`

### Data Storage

- **JSON**: Human-readable, nested structures
- **CSV**: Excel-compatible, flat structure
- **Location**: `data/raw/{site_name}/`

## 📝 Next Steps

1. **Test the scraper** with live data
2. **Add more scrapers** (Avito, Marjane, etc.)
3. **Create transformation scripts** (clean & normalize data)
4. **Build Airflow DAG** for orchestration
5. **Add PostgreSQL loading** scripts

## 🎨 Code Quality

- ✅ Clean inheritance structure
- ✅ Comprehensive error handling
- ✅ Detailed logging with emojis
- ✅ Type hints in docstrings
- ✅ Follows PEP 8 style guide
- ✅ Modular и scalable design
