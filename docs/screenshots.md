# Screenshots Guide

This document describes the recommended screenshots for the project portfolio.

Store screenshots in:

```text
docs/screenshots/
```

## Recommended Screenshots

### 1. Dashboard Overview

- Page: `/`
- Capture: KPI cards, monthly revenue line chart, category pie chart, top products bar chart, recent orders table.
- Why: Shows the product value at a glance.

### 2. Sales Analysis

- Page: `/sales`
- Capture: Revenue/profit trends, payment methods, order status, country/category tables.
- Why: Demonstrates deeper analytical capability.

### 3. Orders Management

- Page: `/orders`
- Capture: Search/filter bar, paginated order table, status badges.
- Why: Shows data-table UX and operational workflows.

### 4. Customer Segmentation

- Page: `/segments`
- Capture: Gaussian Mixture training button, segment distribution chart, segment summary, customer table.
- Why: Demonstrates customer behavior analysis and ML integration.

### 5. Sales Forecasting

- Page: `/forecast`
- Capture: XGBoost training button, MAE/RMSE/R2 metrics, 30-day forecast chart, forecast table.
- Why: Shows predictive analytics and model evaluation.

### 6. CSV Upload

- Page: `/upload`
- Capture: Drag-and-drop upload area, required columns, import summary with processed/inserted/failed counts.
- Why: Demonstrates ETL and data ingestion UX.

### 7. API Documentation

- URL: `http://localhost:8000/docs`
- Capture: Swagger UI with API route groups visible.
- Why: Shows professional API design and auto-generated docs.

## Suggested Filenames

```text
docs/screenshots/dashboard.png
docs/screenshots/sales-analysis.png
docs/screenshots/orders.png
docs/screenshots/customer-segmentation.png
docs/screenshots/sales-forecasting.png
docs/screenshots/upload-dataset.png
docs/screenshots/api-docs.png
```

## How to Capture

1. Start the backend and frontend.
2. Upload `data/processed/online_retail_sales_75k.csv` or seed the sample data.
3. Train the forecasting model from the Forecasting page.
4. Train the segmentation model from the Segmentation page.
5. Capture screenshots in Chrome at a clean zoom level.
6. Save them under `docs/screenshots/`.
7. Link the best screenshots from the main `README.md`.
