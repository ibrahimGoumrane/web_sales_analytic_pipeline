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

### 1. Report Generation (2-3h)

**Create:** `reports/generate_reports.py`

**What it does:**
- Connects to PostgreSQL database
- Generates 4 CSV reports:
  - Category statistics (count, avg price, ratings)
  - Top 50 rated products
  - Biggest discounts
  - Daily summary stats
- Saves to `data/reports/jumia/`

**Update DAG:**
- Add 4th task `generate_reports` to Airflow DAG
- Chain tasks: `scrape → transform → load → reports`

---

### 2. Screenshots & Samples (1h)

**Create folders:**
- `docs/screenshots/` - Airflow UI (successful run, graph view)
- `docs/screenshots/` - Database data (pgAdmin/DBeaver)
- `docs/samples/` - Sample CSV exports (first 100 rows)

**Add to README:**
- Embed screenshots showing working pipeline
- Link to sample data files

---

## 🟡 Optional Enhancements

### 3. Data Visualization (2-3h)

**Create:** `reports/generate_dashboard.py`

**What it does:**
- Interactive HTML dashboard using Plotly
- 4 charts: category distribution, price histogram, ratings, discounts
- Saves to `data/reports/jumia/dashboard.html`

**Add:** `plotly` to requirements.txt

---

### 4. Unit Tests (3-4h)

**Create:** `tests/` folder with test files
- Test scraper functions (URL handling, initialization)
- Test transformer functions (price cleaning, data normalization)
- Run: `pytest tests/`

---

### 5. API Layer (3-4h)

**Create:** `api/main.py` using FastAPI
- Endpoint: `/products` (with filters: category, rating, limit)
- Endpoint: `/stats/categories` (aggregated stats)
- Run: `uvicorn api.main:app --reload`
- Auto docs at: http://localhost:8000/docs

---

### 6. Cloud Deployment (4-6h)

**Options:**
- **Render:** Free PostgreSQL hosting
- **AWS:** RDS + EC2 + S3 (free tier)
- **GCP:** Cloud SQL + Cloud Composer + Storage

---

## 📊 Priority Matrix

| Task | Time | Impact | Priority |
|------|------|--------|----------|
| Report Generation | 2-3h | High | 🔴 Must Do |
| Screenshots | 1h | High | 🔴 Must Do |
| Visualization | 2-3h | Medium | 🟡 Nice to Have |
| Unit Tests | 3-4h | Low | 🟢 Optional |
| API Layer | 3-4h | Low | 🟢 Optional |
| Cloud Deploy | 4-6h | Medium | 🟢 Optional |

---

## 🚀 Quick Start

```bash
# 1. Create folders
mkdir -p reports data/reports/jumia docs/screenshots docs/samples

# 2. Implement reports/generate_reports.py
# 3. Update airflow/dags/sales_etl_dag.py (add 4th task)
# 4. Restart: make restart
# 5. Trigger DAG and verify reports
# 6. Take screenshots
```

**Minimum to portfolio-ready: 3-4 hours**

---

*Updated: Dec 2, 2025*
