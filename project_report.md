# Sales & Customer Analytics Intelligence Platform - Project Report

---

## 1. Executive Summary

This project delivers a full-stack, production-style analytics platform for sales and customer data. It demonstrates backend engineering with FastAPI and SQLAlchemy, frontend development with React and TypeScript, ETL pipelines with pandas, SQL analytics, and applied machine learning with XGBoost and scikit-learn.

---

## 2. Business Problem

Organizations collect sales data in spreadsheets, CSV exports, and transactional systems. Analysts need a repeatable way to clean data, calculate reliable revenue and profit metrics, identify top products/customers/regions, forecast future revenue, and segment customers for targeted actions.

This platform automates the pipeline from raw CSV to actionable dashboard insights.

---

## 3. Technical Solution

### 3.1 Architecture

The system follows a 3-tier architecture:

1. Presentation tier: React SPA with Recharts visualizations.
2. Application tier: FastAPI with service-layer separation.
3. Data tier: PostgreSQL-compatible schema with SQLAlchemy and Alembic.

### 3.2 Backend Design

- FastAPI provides REST APIs and automatic OpenAPI documentation.
- Service modules isolate business logic from route handlers.
- SQLAlchemy 2.x models define relationships, indexes, constraints, and cascade behavior.
- Pydantic v2 schemas validate and serialize API responses.

### 3.3 Database Design

The schema is normalized around:

- customers: one row per unique customer.
- products: one row per unique product.
- orders: one row per order.
- order_items: product lines per order.
- payments: one payment row per order.
- data_import_logs: import audit trail.
- ml_model_runs: trained model metadata and artifact paths.

### 3.4 ETL Pipeline

1. Validate file extension, MIME type, and file size.
2. Read CSV with pandas while preserving key fields as strings.
3. Clean dates, currencies, names, countries, statuses, categories, quantities, and missing values.
4. Remove duplicate order/product rows.
5. Normalize denormalized rows into relational tables.
6. Recalculate order totals after item insertion.
7. Store import logs with processed/inserted/failed counts.

### 3.5 Analytics Logic

Analytics are computed from database records, not hardcoded values:

- KPIs: revenue, profit, orders, customers, AOV, paid/pending revenue.
- Trends: monthly revenue and profit.
- Rankings: top products and customers.
- Geography: sales by country.
- Profit: revenue minus product cost.
- Operational summaries: payment methods and order statuses.

### 3.6 ML Forecasting Logic

- Model: XGBoost Regressor with a log-transformed revenue target.
- Features: calendar fields, lag-1/7/14 revenue, 7/14/30-day rolling revenue, order count, lagged order count.
- Evaluation: time-based train/test split with MAE, RMSE, and R2.
- Prediction: iterative 30-day forecast using prior predictions as lag inputs.
- Persistence: joblib artifact plus `ml_model_runs` database entry.

### 3.7 Customer Segmentation Logic

- Features: RFM metrics per customer, including recency, frequency, monetary value, and AOV.
- Preprocessing: StandardScaler normalization.
- Model: Gaussian Mixture Model with 4 components and full covariance.
- Evaluation: silhouette score, AIC, and BIC.
- Output: readable segment labels such as High Value, Loyal, At Risk, and Low Activity.

### 3.8 Frontend Design

- React Router handles dashboard, analysis, orders, customers, products, segmentation, forecasting, and upload pages.
- Reusable UI components include KPI cards, chart cards, data tables, upload box, loading state, and error state.
- A centralized Axios API client keeps backend access consistent.
- Recharts renders line, bar, and pie charts.
- Tailwind CSS provides responsive styling.

---

## 4. Testing Strategy

| Test File | Coverage |
|-----------|----------|
| `test_health.py` | Health endpoint availability |
| `test_data_cleaning.py` | Date parsing, amount cleaning, status/category normalization, duplicate removal |
| `test_imports.py` | CSV validation, upload endpoint, numeric order numbers |
| `test_analytics.py` | KPI calculation with seeded data |
| `test_dataset_adapters.py` | Online Retail dataset conversion |
| `test_ml_forecasting.py` | Insufficient-data fallback and XGBoost training |
| `test_ml_segmentation.py` | Insufficient-data fallback, RFM recency logic, and Gaussian Mixture training |

Tests use an in-memory SQLite database via SQLAlchemy for fast, isolated execution.

---

## 5. Deployment Strategy

### Local Development

- Docker Compose can run PostgreSQL, backend, and frontend.
- Manual local mode can run backend on SQLite when Docker/PostgreSQL are unavailable.
- Frontend runs with Vite on port 5173.
- Backend runs with Uvicorn on port 8000.

### Production Considerations

- Use a production ASGI server such as Gunicorn with Uvicorn workers.
- Serve the frontend static build through NGINX or a CDN.
- Use managed PostgreSQL.
- Store uploaded CSVs and ML artifacts in object storage.
- Add authentication, background jobs, CI/CD, and cloud deployment.

---

## 6. Limitations

- No authentication or user roles.
- Batch CSV ingestion only.
- ML models retrain manually from the UI/API.
- Forecast quality depends on historical data coverage and missing external signals such as promotions or holidays.

---

## 7. Future Work

- OAuth2/JWT authentication with role-based access.
- Celery + Redis for background ETL and scheduled model retraining.
- Prophet or LightGBM model comparison for forecasting.
- Automated data quality scoring.
- Dashboard exports to PDF/Excel.
- Cloud deployment with managed PostgreSQL and object storage.

---

## 8. Skills Demonstrated

| Domain | Skills |
|--------|--------|
| Backend Engineering | FastAPI, SQLAlchemy 2.x, Pydantic v2, REST API design |
| Data Engineering | pandas, ETL pipelines, data cleaning, deduplication |
| Database Design | PostgreSQL-compatible schema, normalization, indexing, Alembic migrations |
| SQL Analytics | Aggregations, joins, group by, views |
| Machine Learning | XGBoost, Gaussian Mixture Models, feature engineering, model evaluation, artifact management |
| Frontend Engineering | React, TypeScript, Recharts, Tailwind CSS |
| DevOps | Docker, Docker Compose, Makefile, environment configuration |
| Testing | pytest, test fixtures, in-memory test database |
| Documentation | README, project report, API contracts, architecture docs |

---

## 9. Conclusion

This platform demonstrates the ability to design, build, test, and document a realistic analytics product from scratch. It covers the full data lifecycle: ingestion, cleaning, storage, analysis, prediction, and visualization.
