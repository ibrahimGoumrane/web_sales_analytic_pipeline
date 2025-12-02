# Web Sales Analytics ETL Pipeline

> End-to-end data engineering project showcasing ETL pipelines, Apache Airflow orchestration, and web scraping from Jumia.ma

## Overview

This project demonstrates a production-ready ETL pipeline that extracts product and pricing data from Jumia.ma, transforms it into analytics-ready formats, and loads it into a PostgreSQL data warehouse. The entire pipeline is orchestrated with Apache Airflow and containerized with Docker for reliable, scheduled execution.

## Features

### 🔍 Data Extraction

- Web scraping with BeautifulSoup and Requests
- Automatic category discovery and pagination handling
- Extracts 1000+ products per category from Jumia.ma
- Raw data storage in JSON/CSV format
- Intelligent retry logic and rate limiting

### 🔄 Data Transformation

- Data cleaning with Pandas:
  - Price normalization (removes currency, handles decimals)
  - Discount percentage cleaning
  - Rating and review count standardization
  - Boolean conversion for official store badges
  - Date/time handling

### 💾 Data Loading

- PostgreSQL data warehouse with two databases:
  - `airflow` — Airflow metadata
  - `sales_analytics` — Product data warehouse
- Automated database and schema creation
- Conflict handling with UNIQUE constraints
- Idempotent pipeline tasks for safe re-runs

### ⚙️ Workflow Orchestration

Fully orchestrated with Apache Airflow:

- `scrape_jumia` — Extract products from Jumia.ma
- `transform_jumia` — Clean and normalize data
- `load_jumia` — Load to PostgreSQL warehouse
- Daily scheduling with retry logic
- Task dependency management

## Tech Stack

| Component            | Technology               |
| -------------------- | ------------------------ |
| **Orchestration**    | Apache Airflow 2.8.1     |
| **Web Scraping**     | BeautifulSoup4, Requests |
| **Database**         | PostgreSQL 13            |
| **Data Processing**  | Pandas                   |
| **Containerization** | Docker & Docker Compose  |
| **Storage**          | Local filesystem         |
| **Python**           | 3.8+                     |

## Project Structure

```
web_sales_analytic_pipeline/
│
├── airflow/
│   └── dags/
│       └── sales_etl_dag.py          # Main DAG definition
│
├── scraping/
│   ├── base.py                       # Abstract base scraper class
│   ├── main.py                       # Scraper orchestrator
│   ├── utils.py                      # URL handling utilities
│   └── jumia/
│       └── main.py                   # Jumia scraper implementation
│
├── transform/
│   ├── base.py                       # Abstract base transformer
│   ├── main.py                       # Transform orchestrator
│   └── jumia/
│       └── main.py                   # Jumia data cleaner
│
├── load/
│   └── load_postgres.py              # PostgreSQL loader
│
├── data/
│   ├── raw/jumia/                    # Raw scraped data (JSON/CSV)
│   ├── processed/jumia/              # Cleaned data (CSV)
│   └── reports/jumia/                # Generated reports
│
├── html_structure/
│   └── jumia/                        # HTML samples for reference
│
├── logs/                             # Application logs
├── docker-compose.yaml               # Container orchestration
├── Makefile                          # Build automation
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables
├── StartupDocs.md                    # Quick start guide
└── README.md                         # This file
```

## Getting Started

### Prerequisites

- **Docker Desktop** 20.10+
- **Python** 3.8+
- **Make** (Windows: gnuwin32.sourceforge.net)
- **Git**

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/ibrahimGoumrane/web_sales_analytic_pipeline.git
   cd web_sales_analytic_pipeline
   ```

2. **Ensure Docker Desktop is running**

   ```bash
   docker --version
   docker ps
   ```

3. **Start the entire pipeline**

   ```bash
   make all
   ```

   This will:

   - Start PostgreSQL database
   - Initialize Airflow (creates admin user)
   - Start Airflow webserver and scheduler
   - Wait ~2-3 minutes for initialization

4. **Access Airflow UI**

   - URL: http://localhost:8085
   - Username: `admin`
   - Password: `admin`

5. **Run the pipeline**
   - Find `jumia_daily_etl` DAG in the UI
   - Toggle switch to enable
   - Click ▶️ Play → Trigger DAG
   - Monitor execution (Green = Success)

### Verify Installation

```bash
# Check services are running
make ps

# View logs
make logs

# Check database
docker exec -it web_sales_analytic_pipeline-postgres-1 psql -U airflow -d sales_analytics
# Inside psql:
SELECT COUNT(*) FROM products WHERE website = 'jumia';
\q
```

### Available Commands

```bash
make help          # Show all available commands
make up            # Start all services
make down          # Stop all services
make restart       # Restart services
make logs          # View all logs
make clean         # Remove all data and reset
make ps            # Check container status
```

For detailed setup instructions, see [StartupDocs.md](StartupDocs.md).

## Data Output

### Database Schema

**Database:** `sales_analytics`  
**Table:** `products`

| Column            | Type          | Description            |
| ----------------- | ------------- | ---------------------- |
| id                | SERIAL        | Primary key            |
| website           | VARCHAR(50)   | Source website (jumia) |
| sku               | VARCHAR(100)  | Product SKU            |
| name              | TEXT          | Product name           |
| url               | TEXT          | Product URL            |
| current_price     | NUMERIC(10,2) | Current price          |
| old_price         | NUMERIC(10,2) | Original price         |
| discount          | NUMERIC(5,2)  | Discount percentage    |
| rating            | NUMERIC(3,2)  | Product rating (0-5)   |
| review_count      | INTEGER       | Number of reviews      |
| is_official_store | BOOLEAN       | Official store badge   |
| image_url         | TEXT          | Product image URL      |
| scraped_at        | TIMESTAMP     | Scraping timestamp     |
| created_at        | TIMESTAMP     | Record creation time   |

### File Outputs

- **`data/raw/jumia/`** — Raw scraped data (JSON/CSV)
- **`data/processed/jumia/`** — Cleaned product data (CSV)
- **`logs/`** — Scraper and transformation logs

## Pipeline Execution

The DAG runs daily with the following workflow:

1. **Scrape Jumia** (Task: `scrape_jumia`)

   - Discovers categories automatically
   - Scrapes 1000 products per category
   - Saves raw data to `data/raw/jumia/`

2. **Transform Data** (Task: `transform_jumia`)

   - Cleans prices and percentages
   - Normalizes ratings and reviews
   - Saves to `data/processed/jumia/`

3. **Load to Database** (Task: `load_jumia`)
   - Inserts cleaned data into PostgreSQL
   - Handles duplicates with UNIQUE constraints
   - Creates `sales_analytics` database automatically

## Skills Demonstrated

- ✅ **ETL Pipeline Design** — Complete Extract-Transform-Load workflow
- ✅ **Apache Airflow** — DAG creation, task dependencies, scheduling
- ✅ **Web Scraping** — BeautifulSoup, pagination, category discovery
- ✅ **Data Engineering** — Pandas transformations, data cleaning
- ✅ **Database Design** — PostgreSQL schema, indexing, constraints
- ✅ **Containerization** — Docker Compose multi-service orchestration
- ✅ **DevOps** — Makefile automation, environment management
- ✅ **Code Organization** — Abstract base classes, modular design

## Future Enhancements

See [Recommendations.md](Recommendations.md) for planned improvements:

- Report generation and analytics
- Data visualization dashboards
- Additional e-commerce site support
- Cloud deployment (AWS/GCP/Azure)
- API layer for data access

## Connection Details

**Airflow Web UI:**

- URL: http://localhost:8085
- Username: `admin`
- Password: `admin`

**PostgreSQL:**

- Host: `localhost`
- Port: `5432`
- User: `airflow`
- Password: `airflow`
- Databases: `airflow`, `sales_analytics`

## Troubleshooting

Common issues and solutions:

| Issue                | Solution                                          |
| -------------------- | ------------------------------------------------- |
| Port 8085 in use     | `netstat -ano \| findstr :8085` then kill process |
| Docker not running   | Start Docker Desktop and wait for ready           |
| DAG not visible      | `make restart` to refresh Airflow                 |
| Services won't start | `make clean` then `make all` for fresh start      |

For detailed troubleshooting, see [StartupDocs.md](StartupDocs.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

---

**Built for data engineering learning and portfolio development**  
_Showcasing ETL pipelines, Airflow orchestration, and modern data engineering practices_
