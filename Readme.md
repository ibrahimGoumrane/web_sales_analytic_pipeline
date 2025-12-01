# Web Sales Analytics ETL Pipeline

> A complete end-to-end data engineering project for learning ETL/ELT pipelines, Apache Airflow orchestration, and web scraping techniques.

## Overview

This project demonstrates a production-ready ETL pipeline that extracts product and pricing data from e-commerce websites, transforms it into analytics-ready formats, and loads it into a PostgreSQL data warehouse. The pipeline is fully orchestrated with Apache Airflow for reliable, scheduled execution.

## Features

### 🔍 Data Extraction
- **Static scraping** with BeautifulSoup for product catalogs
- **Dynamic scraping** with Selenium for JavaScript-rendered pages
- Raw data storage in JSON/CSV format

### 🔄 Data Transformation
- Data cleaning with Pandas (null handling, price normalization, category mapping)
- Analytics-ready tables:
  - `products_cleaned`
  - `daily_prices`
  - `product_category_stats`

### 💾 Data Loading
- PostgreSQL data warehouse integration
- Automated schema creation
- Idempotent pipeline tasks for safe re-runs

### ⚙️ Workflow Orchestration
Fully orchestrated with Apache Airflow:
- `extract_products` — Scrape product catalog
- `extract_daily_prices` — Scrape price data with Selenium
- `clean_transform` — Apply data transformations
- `load_to_postgres` — Load to data warehouse
- `generate_reports` — Export analytics as CSV

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Orchestration** | Apache Airflow |
| **Web Scraping** | BeautifulSoup, Requests, Selenium |
| **Database** | PostgreSQL |
| **Data Processing** | Pandas |
| **Storage** | Local filesystem / S3 (optional) |
| **Visualization** | PowerBI / Metabase / Grafana (optional) |

## Project Structure

```
web_sales_analytic_pipeline/
│
├── airflow/
│   ├── dags/
│   │   └── sales_etl_dag.py
│   └── docker-compose.yaml
│
├── scraping/
│   ├── extract_catalog.py
│   ├── extract_price_history.py
│   └── utils.py
│
├── transform/
│   └── clean_transform.py
│
├── load/
│   ├── load_postgres.py
│   └── create_schema.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── reports/
│
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Chrome/Chromium (for Selenium)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/web_sales_analytic_pipeline.git
   cd web_sales_analytic_pipeline
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup PostgreSQL database**
   ```sql
   CREATE DATABASE salesdb;
   ```
   
   Initialize the schema:
   ```bash
   python load/create_schema.py
   ```

4. **Configure Apache Airflow**
   ```bash
   # Initialize Airflow database
   airflow db init
   
   # Create admin user
   airflow users create \
     --username admin \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com
   ```

5. **Start Airflow services**
   ```bash
   # Terminal 1
   airflow webserver -p 8080
   
   # Terminal 2
   airflow scheduler
   ```

### Running the Pipeline

1. Navigate to the Airflow UI at `http://localhost:8080`
2. Enable the `sales_etl_pipeline` DAG
3. Trigger manually or configure scheduling

## Outputs

The pipeline generates the following analytics:

- **`reports/price_history.csv`** — Historical price trends
- **`processed/products_cleaned.csv`** — Cleaned product catalog
- **`reports/category_stats.csv`** — Category-level statistics

## Future Enhancements

### 📊 Dashboards
Build interactive dashboards with Metabase or PowerBI:
- Price trends by category
- Product pricing analytics (min/max/avg)
- Daily scraping metrics

### ☁️ Cloud Deployment
Deploy to cloud infrastructure:
- Host PostgreSQL on Render (free tier)
- Use Google Cloud Storage for data lakes
- Deploy Airflow on Railway or Oracle Cloud

### 🚀 API Layer
Expose analytics via RESTful API:
- Build with FastAPI
- Enable real-time querying
- Add authentication and rate limiting

## Learning Outcomes

This project teaches you:

- ✅ Designing production ETL/ELT pipelines
- ✅ Orchestrating workflows with Apache Airflow
- ✅ Web scraping (static and dynamic content)
- ✅ Data cleaning and transformation
- ✅ Building data warehouses with PostgreSQL
- ✅ Creating scalable project architectures

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

---

**Built with ❤️ for data engineering learning and portfolio development**