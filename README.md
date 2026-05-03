<p align="center">
  <img src="docs/banner.svg" alt="Sales & Customer Analytics Intelligence Platform" width="100%"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/XGBoost-3.2-FF6600?style=flat-square" alt="XGBoost"/>
  <img src="https://img.shields.io/badge/Gaussian_Mixture-Scikit--learn-F7931E?style=flat-square" alt="Gaussian Mixture"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-2.x-CC2927?style=flat-square" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="License"/>
</p>

<p align="center">
  A full-stack portfolio project that <strong>turns raw sales datasets into relational data, analytics dashboards, XGBoost revenue forecasts, and Gaussian Mixture customer segments</strong>.
</p>

---

## Screenshots & Visuals

<details open>
<summary><strong>Dashboard Overview — KPIs, revenue trends, category/product/country charts</strong></summary>
<br>

![Dashboard Overview](docs/screenshots/dashboard.png)

</details>

<details>
<summary><strong>Sales Analysis — revenue, profit, payment methods, order status</strong></summary>
<br>

![Sales Analysis](docs/screenshots/sales-analysis.png)

</details>

<details>
<summary><strong>Orders — search, filters, pagination, status badges</strong></summary>
<br>

![Orders](docs/screenshots/orders.png)

</details>

<details>
<summary><strong>Customers — customer table with country and segment data</strong></summary>
<br>

![Customers](docs/screenshots/customers.png)

</details>

<details>
<summary><strong>Customer Segmentation — Gaussian Mixture RFM segments</strong></summary>
<br>

![Customer Segmentation](docs/screenshots/customer-segmentation.png)

</details>

<details>
<summary><strong>Sales Forecasting — XGBoost metrics and 30-day forecast</strong></summary>
<br>

![Sales Forecasting](docs/screenshots/sales-forecasting.png)

</details>

<details>
<summary><strong>Upload Dataset — CSV import summary and ETL validation</strong></summary>
<br>

![Upload Dataset](docs/screenshots/upload-dataset.png)

</details>

<details>
<summary><strong>Architecture & Data Flow</strong></summary>
<br>

![Architecture](assets/github/architecture.svg)

![Data Flow](assets/github/data-flow.svg)

</details>

---

## Features

### Data Ingestion & ETL

| | |
|---|---|
| CSV upload | Drag-and-drop import for denormalized sales datasets |
| Validation | Required-column checks, file type validation, size limit handling |
| Cleaning | Dates, currencies, customer names, countries, statuses, categories |
| Deduplication | Duplicate removal using `order_number + product_code` |
| Normalization | Loads data into customers, orders, products, order_items, and payments |
| Import logging | Stores processed, inserted, failed rows, warnings, and errors |

### Analytics Dashboard

| | |
|---|---|
| KPI cards | Revenue, profit, orders, customers, products sold, AOV |
| Revenue trends | Monthly revenue and profit time-series charts |
| Product analysis | Top products, categories, quantity sold, profit |
| Customer analysis | Top customers, spend, order frequency, segments |
| Geography | Sales by country with revenue, orders, and customer counts |
| Payments | Payment method and order status summaries |

### Machine Learning

| | |
|---|---|
| Forecasting model | XGBoost Regressor for 30-day revenue forecast |
| Forecast features | Calendar fields, lag revenue, rolling means, order-volume features |
| Forecast metrics | MAE, RMSE, R2, training rows |
| Segmentation model | Gaussian Mixture Model on RFM customer features |
| Segment features | Recency, frequency, monetary value, average order value |
| Segment metrics | Silhouette score, AIC, BIC, training rows |

### Frontend UX

| | |
|---|---|
| Dashboard pages | Dashboard, Sales Analysis, Orders, Customers, Products, Segmentation, Forecasting, Upload |
| Visualizations | Recharts line, bar, and pie charts |
| Tables | Searchable/filterable operational tables |
| States | Loading states, error states, empty states, import summaries |
| API client | Centralized Axios client with environment-based base URL |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2 |
| Data Engineering | pandas, numpy, custom ETL and dataset adapter scripts |
| Machine Learning | XGBoost, scikit-learn, joblib |
| Database | PostgreSQL in Docker, SQLite for local no-Docker development |
| Frontend | React 18, TypeScript, Vite, Axios, React Router |
| Visualization | Recharts, Tailwind CSS, Lucide React |
| Infrastructure | Docker Compose, GitHub Actions CI, Makefile |
| Testing | pytest, FastAPI TestClient, in-memory SQLite fixtures |

---

## Quick Start

### Local without Docker

**1. Backend**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env -Force
python -c "from app.db.init_db import init_db; init_db(); print('SQLite schema created')"
python -m app.db.seed
uvicorn app.main:app --reload
# -> http://localhost:8000/docs
```

**2. Frontend**

```powershell
cd frontend
npm install
Copy-Item .env.example .env -Force
npm run dev
# -> http://localhost:5173
```

### Docker full stack

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

Services:

```text
Frontend: http://localhost:5173
Backend API: http://localhost:8000
Swagger Docs: http://localhost:8000/docs
PostgreSQL: localhost:5432
```

---

## Real Dataset Workflow

The project includes an adapter for the public Online Retail dataset format:

```text
InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
```

Convert the raw Excel file into the platform import schema:

```powershell
cd backend
python -m scripts.convert_online_retail --input ../data/raw/online_retail.xlsx --output ../data/processed/online_retail_sales.csv
```

Create a smaller 75k-row demo file:

```powershell
cd backend
python -m scripts.convert_online_retail --input ../data/raw/online_retail.xlsx --output ../data/processed/online_retail_sales_75k.csv --max-rows 75000
```

Then upload the converted CSV from the Upload Dataset page.

Raw and processed datasets are intentionally ignored by git.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Backend health check |
| `POST` | `/api/imports/sales` | Upload and import sales CSV |
| `GET` | `/api/orders` | List orders with filters and pagination |
| `GET` | `/api/customers` | List customers |
| `GET` | `/api/products` | List products |
| `GET` | `/api/analytics/kpis` | KPI summary |
| `GET` | `/api/analytics/monthly-sales` | Monthly revenue and profit |
| `GET` | `/api/analytics/top-products` | Top products by revenue |
| `GET` | `/api/analytics/top-customers` | Top customers by spend |
| `GET` | `/api/analytics/sales-by-country` | Country revenue breakdown |
| `GET` | `/api/analytics/sales-by-category` | Category revenue breakdown |
| `GET` | `/api/analytics/payment-methods` | Payment method summary |
| `GET` | `/api/analytics/order-status` | Order status summary |
| `GET` | `/api/analytics/profit-summary` | Profit and margin summary |
| `POST` | `/api/ml/train-forecast` | Train XGBoost forecast model |
| `GET` | `/api/ml/sales-forecast` | Get 30-day revenue forecast |
| `POST` | `/api/ml/train-segmentation` | Train Gaussian Mixture model |
| `GET` | `/api/ml/customer-segments` | Get customer segment assignments |

Interactive docs are available at:

```text
http://localhost:8000/docs
```

---

## Project Structure

```text
sales-customer-analytics-platform/
├── .github/workflows/ci.yml
├── assets/github/
│   ├── architecture.svg
│   └── data-flow.svg
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   └── ml/
│   │   └── utils/
│   ├── alembic/
│   ├── sample_data/
│   ├── scripts/
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── banner.svg
│   ├── architecture.md
│   ├── api_contract.md
│   ├── data_dictionary.md
│   └── screenshots.md
├── frontend/
│   └── src/
│       ├── api/
│       ├── components/
│       ├── pages/
│       ├── types/
│       └── utils/
├── notebooks/
├── sql/
├── docker-compose.yml
├── Makefile
├── project_report.md
└── README.md
```

---

## Tests & Verification

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -v
```

Frontend:

```powershell
cd frontend
npm run build
npm audit --audit-level=moderate
```

Current local verification:

```text
Backend tests: 23 passed
Frontend build: passed
Frontend audit: 0 vulnerabilities
```

---

## Environment Variables

### Backend

```env
APP_NAME=Sales Analytics API
APP_VERSION=1.0.0
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/sales_db
SQLITE_DATABASE_URL=sqlite:///./sales_test.db
UPLOAD_DIR=uploads
ARTIFACT_DIR=artifacts
MAX_UPLOAD_SIZE_MB=100
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://frontend:5173
```

### Frontend

```env
VITE_API_BASE_URL=/api
VITE_API_PROXY_TARGET=http://localhost:8000
```

---

## GitHub Publishing Checklist

Do not commit:

```text
backend/.env
frontend/.env
backend/.venv/
frontend/node_modules/
frontend/dist/
backend/sales_dev.db
backend/artifacts/
backend/uploads/
data/raw/
data/processed/
```

Publish:

```powershell
git init
git branch -M main
git add .
git status --short
git commit -m "Initial sales customer analytics platform"
git remote add origin https://github.com/Stelios-developer/sales-customer-analytics-platform.git
git push -u origin main
```

Recommended repository topics:

```text
fastapi, react, typescript, postgresql, sqlalchemy, data-engineering,
etl, analytics-dashboard, machine-learning, xgboost,
customer-segmentation, sales-analytics
```

---

## Interview Summary

```text
I built a full-stack sales analytics platform with FastAPI, React, SQLAlchemy,
PostgreSQL-compatible models, a pandas ETL pipeline, SQL-backed analytics APIs,
XGBoost revenue forecasting, and Gaussian Mixture customer segmentation based
on RFM features.
```

---

## License

MIT © [Stelios](https://github.com/Stelios-developer)
