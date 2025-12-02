# 📋 Recommendations - Complete the Pipeline

## ✅ Done
- Web scraping, transformation, loading
- Airflow DAG (3 tasks)
- Docker setup, documentation

## ❌ Missing
- Report generation
- Screenshots/samples
- Data visualization

---

## 🔴 CRITICAL Tasks

### 1. Report Generation

Create `reports/generate_reports.py`:

```python
import pandas as pd
import psycopg2
import os
from datetime import datetime

def generate_reports():
    """Generate analytics reports from warehouse data."""

    # Connect to database
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="sales_analytics",
        user="airflow",
        password="airflow"
    )

    output_dir = "data/reports/jumia"
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")

    # Report 1: Category Statistics
    query_category = """
    SELECT
        category,
        COUNT(*) as product_count,
        AVG(current_price) as avg_price,
        MIN(current_price) as min_price,
        MAX(current_price) as max_price,
        AVG(rating) as avg_rating,
        AVG(discount) as avg_discount
    FROM products
    WHERE website = 'jumia' AND category IS NOT NULL
    GROUP BY category
    ORDER BY product_count DESC;
    """
    df_category = pd.read_sql(query_category, conn)
    df_category.to_csv(f"{output_dir}/category_stats_{date_str}.csv", index=False)

    # Report 2: Top Rated Products
    query_top_rated = """
    SELECT name, brand, current_price, rating, review_count, url
    FROM products
    WHERE website = 'jumia' AND rating IS NOT NULL
    ORDER BY rating DESC, review_count DESC
    LIMIT 50;
    """
    df_top_rated = pd.read_sql(query_top_rated, conn)
    df_top_rated.to_csv(f"{output_dir}/top_rated_products_{date_str}.csv", index=False)

    # Report 3: Biggest Discounts
    query_discounts = """
    SELECT name, brand, old_price, current_price, discount, url
    FROM products
    WHERE website = 'jumia' AND discount IS NOT NULL AND discount > 0
    ORDER BY discount DESC
    LIMIT 50;
    """
    df_discounts = pd.read_sql(query_discounts, conn)
    df_discounts.to_csv(f"{output_dir}/biggest_discounts_{date_str}.csv", index=False)

    # Report 4: Daily Summary
    query_summary = """
    SELECT
        DATE(scraped_at) as scrape_date,
        COUNT(*) as total_products,
        AVG(current_price) as avg_price,
        COUNT(CASE WHEN discount > 0 THEN 1 END) as products_on_sale,
        AVG(CASE WHEN discount > 0 THEN discount END) as avg_discount_percent
    FROM products
    WHERE website = 'jumia'
    GROUP BY DATE(scraped_at)
    ORDER BY scrape_date DESC;
    """
    df_summary = pd.read_sql(query_summary, conn)
    df_summary.to_csv(f"{output_dir}/daily_summary_{date_str}.csv", index=False)

    conn.close()
    print(f"✅ Generated 4 reports in {output_dir}")

if __name__ == "__main__":
    generate_reports()
```

Add 4th task to `airflow/dags/sales_etl_dag.py`:

```python
def generate_reports():
    from reports import generate_reports as gen
    gen.generate_reports()

t4 = PythonOperator(task_id='generate_reports', python_callable=generate_reports)
t1 >> t2 >> t3 >> t4
```

**Time:** 2-3 hours

---

### 2. Screenshots & Samples

Create folders:
- `docs/screenshots/` - Airflow UI, database data
- `docs/samples/` - Sample CSV files (100 rows)

**Time:** 1 hour

---

## 🟡 Optional Enhancements

### 3. Data Visualization

Create `reports/generate_dashboard.py`:

```python
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_dashboard():
    """Generate interactive HTML dashboard."""

    conn = psycopg2.connect(
        host="localhost", port=5432,
        database="sales_analytics", user="airflow", password="airflow"
    )

    # Fetch data
    df = pd.read_sql("SELECT * FROM products WHERE website = 'jumia'", conn)
    conn.close()

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Products by Category',
            'Price Distribution',
            'Rating Distribution',
            'Discount Analysis'
        )
    )

    # Chart 1: Category counts
    category_counts = df['category'].value_counts().head(10)
    fig.add_trace(
        go.Bar(x=category_counts.index, y=category_counts.values),
        row=1, col=1
    )

    # Chart 2: Price histogram
    fig.add_trace(
        go.Histogram(x=df['current_price'].dropna()),
        row=1, col=2
    )

    # Chart 3: Rating distribution
    fig.add_trace(
        go.Histogram(x=df['rating'].dropna()),
        row=2, col=1
    )

    # Chart 4: Discount scatter
    fig.add_trace(
        go.Scatter(
            x=df['old_price'],
            y=df['current_price'],
            mode='markers',
            marker=dict(color=df['discount'], colorscale='Viridis')
        ),
        row=2, col=2
    )

    fig.update_layout(height=800, showlegend=False, title_text="Jumia Sales Analytics Dashboard")
    fig.write_html("data/reports/jumia/dashboard.html")
    print("✅ Dashboard generated: data/reports/jumia/dashboard.html")

if __name__ == "__main__":
    create_dashboard()
```

**Add to requirements.txt:**

```
plotly
```

**Estimated Time:** 2-3 hours

---

### 4. Add Error Monitoring & Alerts ⭐

**Why:** Shows production-ready thinking about reliability.

**What to implement:**

**Option 1: Email Alerts (Airflow built-in)**

Update `docker-compose.yaml`:

```yaml
environment:
  AIRFLOW__SMTP__SMTP_HOST: smtp.gmail.com
  AIRFLOW__SMTP__SMTP_STARTTLS: "True"
  AIRFLOW__SMTP__SMTP_SSL: "False"
  AIRFLOW__SMTP__SMTP_USER: your-email@gmail.com
  AIRFLOW__SMTP__SMTP_PASSWORD: your-app-password
  AIRFLOW__SMTP__SMTP_PORT: 587
  AIRFLOW__SMTP__SMTP_MAIL_FROM: airflow@example.com
```

Update DAG default_args:

```python
default_args = {
    'email': ['your-email@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
}
```

**Option 2: Logging Metrics**

Create `monitoring/metrics.py`:

```python
import psycopg2
from datetime import datetime

def log_metrics(website, products_scraped, success=True, error_msg=None):
    """Log pipeline execution metrics."""
    conn = psycopg2.connect(
        host="localhost", port=5432,
        database="sales_analytics", user="airflow", password="airflow"
    )

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_metrics (
            id SERIAL PRIMARY KEY,
            website VARCHAR(50),
            run_date TIMESTAMP,
            products_scraped INTEGER,
            success BOOLEAN,
            error_message TEXT
        )
    """)

    cur.execute("""
        INSERT INTO pipeline_metrics
        (website, run_date, products_scraped, success, error_message)
        VALUES (%s, %s, %s, %s, %s)
    """, (website, datetime.now(), products_scraped, success, error_msg))

    conn.commit()
    conn.close()
```

**Estimated Time:** 2 hours

---

## 🟢 OPTIONAL - Nice to Have

### 5. Add Unit Tests ⭐

**Why:** Shows professional software engineering practices.

**What to implement:**

Create `tests/test_scraper.py`:

```python
import pytest
from scraping.jumia import Jumia
from scraping.utils import handle_url

def test_handle_url_relative():
    result = handle_url('/products/phone', 'https://jumia.ma')
    assert result == 'https://jumia.ma/products/phone'

def test_handle_url_absolute():
    result = handle_url('https://jumia.ma/products', 'https://jumia.ma')
    assert result == 'https://jumia.ma/products'

def test_jumia_initialization():
    scraper = Jumia()
    assert scraper.site == 'jumia'
    assert scraper.base_url == 'https://www.jumia.ma'
    assert scraper.categories == []
    assert scraper.products == []
```

Create `tests/test_transform.py`:

```python
import pytest
import pandas as pd
from transform.jumia import CleanDataJumia

def test_clean_price():
    cleaner = CleanDataJumia()
    assert cleaner._clean_price('1,229.00 Dhs') == 1229.00
    assert cleaner._clean_price('500 Dhs') == 500.00
    assert cleaner._clean_price(None) is None

def test_clean_numeric():
    cleaner = CleanDataJumia()
    assert cleaner._clean_numeric('43%') == 43.0
    assert cleaner._clean_numeric('4.5') == 4.5
    assert cleaner._clean_numeric(None) is None
```

**Run tests:**

```bash
pip install pytest
pytest tests/
```

**Estimated Time:** 3-4 hours

---

### 6. Add API Layer ⭐

**Why:** Makes your data accessible via REST API.

**What to implement:**

Create `api/main.py`:

```python
from fastapi import FastAPI, Query
import psycopg2
import pandas as pd

app = FastAPI(title="Jumia Analytics API")

def get_db():
    return psycopg2.connect(
        host="localhost", port=5432,
        database="sales_analytics", user="airflow", password="airflow"
    )

@app.get("/products")
def get_products(
    limit: int = Query(100, le=1000),
    category: str = None,
    min_rating: float = None
):
    """Get products with filters."""
    conn = get_db()
    query = "SELECT * FROM products WHERE website = 'jumia'"

    if category:
        query += f" AND category = '{category}'"
    if min_rating:
        query += f" AND rating >= {min_rating}"

    query += f" LIMIT {limit}"

    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_dict(orient='records')

@app.get("/stats/categories")
def get_category_stats():
    """Get statistics by category."""
    conn = get_db()
    query = """
    SELECT category, COUNT(*) as count, AVG(current_price) as avg_price
    FROM products WHERE website = 'jumia' AND category IS NOT NULL
    GROUP BY category
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_dict(orient='records')
```

**Run:**

```bash
pip install fastapi uvicorn
uvicorn api.main:app --reload
# Access: http://localhost:8000/docs
```

**Estimated Time:** 3-4 hours

---

### 7. Cloud Deployment ⭐

**Why:** Shows you can deploy to production environments.

**Options:**

**Option A: Render (Free Tier)**

- Deploy PostgreSQL database
- Update connection strings in code
- Keep Airflow local or use Render

**Option B: AWS (Free Tier)**

- RDS for PostgreSQL
- EC2 for Airflow
- S3 for data storage
- CloudWatch for monitoring

**Option C: Google Cloud Platform**

- Cloud SQL for PostgreSQL
- Cloud Composer (managed Airflow)
- Cloud Storage for data

**Estimated Time:** 4-6 hours (varies by platform)

---

## 📊 Priority Matrix

| Task                | Impact | Effort | Priority     | Status         |
| ------------------- | ------ | ------ | ------------ | -------------- |
| Report Generation   | High   | Low    | 🔴 Critical  | ❌ Not Started |
| Screenshots/Samples | High   | Low    | 🔴 Critical  | ❌ Not Started |
| Data Visualization  | Medium | Medium | 🟡 Important | ❌ Not Started |
| Error Monitoring    | Medium | Low    | 🟡 Important | ❌ Not Started |
| Unit Tests          | Low    | High   | 🟢 Optional  | ❌ Not Started |
| API Layer           | Low    | Medium | 🟢 Optional  | ❌ Not Started |
| Cloud Deployment    | Medium | High   | 🟢 Optional  | ❌ Not Started |

---

## 🎯 Recommended Implementation Order

### Week 1 (Portfolio-Ready Minimum)

1. ✅ Day 1-2: Implement report generation
2. ✅ Day 3: Create and add screenshots
3. ✅ Day 4: Generate sample outputs
4. ✅ Day 5: End-to-end testing

### Week 2 (Enhanced Portfolio)

5. ⭐ Day 6-7: Add data visualization dashboard
6. ⭐ Day 8: Add error monitoring
7. ⭐ Day 9-10: Documentation polish and demo video

### Week 3+ (Advanced Features)

8. 💡 Add unit tests
9. 💡 Build API layer
10. 💡 Deploy to cloud

---

## 📝 Definition of "Done"

Your pipeline is fully functional when:

- [x] All 3 ETL tasks run successfully
- [ ] 4th report generation task added and working
- [ ] At least 3 different reports generated
- [ ] Screenshots showing successful execution
- [ ] Sample data files available
- [ ] README updated with sample outputs
- [ ] No errors in Airflow UI
- [ ] Data visible in PostgreSQL
- [ ] Can run `make all` and get working pipeline
- [ ] Documentation matches actual implementation

---

## 🚀 Quick Start (Today)

Start with the highest impact, lowest effort task:

```bash
# 1. Create reports directory structure
mkdir -p reports data/reports/jumia docs/screenshots docs/samples

# 2. Copy the generate_reports.py code above
# 3. Add 4th task to DAG
# 4. Test: make restart
# 5. Trigger DAG and verify reports are created
# 6. Take screenshots
# 7. Update README with outputs section
```

**Time to portfolio-ready: ~8-12 hours total** 🎯

---

_Last Updated: December 2, 2025_
_Status: Ready for implementation_
