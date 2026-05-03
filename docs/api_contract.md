# API Contract

## Base URL

Use the backend origin plus `/api`, for example `http://localhost:8000/api` in local development.

## Authentication

Currently, the API is open (no authentication). Future versions will add JWT Bearer tokens.

## Content-Type

All requests and responses use `application/json` unless otherwise specified.

## Common Response Patterns

Success responses are endpoint-specific JSON objects or arrays. ML and import endpoints include a `status` field; analytics endpoints return plain typed payloads.

### Error
```json
{
  "detail": "Error message here"
}
```

---

## Endpoints

### Health

**GET** `/health`

**Response:**
```json
{
  "status": "ok",
  "service": "Sales Analytics API",
  "version": "1.0.0"
}
```

---

### Imports

**POST** `/api/imports/sales`

**Content-Type:** `multipart/form-data`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | File | Yes | CSV file (max 20MB) |

**Response:**
```json
{
  "status": "success",
  "filename": "sales_data.csv",
  "rows_processed": 40,
  "rows_inserted": 40,
  "rows_failed": 0,
  "warnings": ["5 missing customer cities were set to Unknown"],
  "errors": []
}
```

---

### Orders

**GET** `/api/orders`

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| search | string | - | Search order number or customer name |
| status | string | - | Filter by order status |
| country | string | - | Filter by country |
| date_from | date | - | Filter from date (YYYY-MM-DD) |
| date_to | date | - | Filter to date (YYYY-MM-DD) |
| sort_by | string | order_date | Sort column |
| sort_order | string | desc | asc or desc |
| page | integer | 1 | Page number |
| page_size | integer | 20 | Items per page |

**Response:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

---

### Analytics

**GET** `/api/analytics/kpis`

**Query Parameters:**
| Name | Type | Description |
|------|------|-------------|
| date_from | date | Optional start date |
| date_to | date | Optional end date |

**Response:**
```json
{
  "total_revenue": 450000.00,
  "total_profit": 135000.00,
  "number_of_orders": 1200,
  "number_of_customers": 340,
  "number_of_products": 45,
  "average_order_value": 375.00,
  "conversion_proxy": 92.50,
  "paid_revenue": 416250.00,
  "pending_revenue": 33750.00,
  "top_product": "Laptop Pro 14",
  "top_customer": "Maria Papadopoulou",
  "best_country": "Germany"
}
```

---

### Machine Learning

**POST** `/api/ml/train-forecast`

**Response:**
```json
{
  "model_name": "RandomForestRegressor",
  "mae": 245.30,
  "rmse": 390.80,
  "r2": 0.82,
  "training_rows": 180
}
```

**GET** `/api/ml/sales-forecast`

**Response:**
```json
{
  "status": "success",
  "forecast": [
    { "date": "2024-07-01", "predicted_revenue": 1320.50 },
    ...
  ]
}
```

**POST** `/api/ml/train-segmentation`

**Response:**
```json
{
  "model_name": "KMeans",
  "n_clusters": 4,
  "silhouette_score": 0.65,
  "training_rows": 120
}
```

**GET** `/api/ml/customer-segments`

**Response:**
```json
{
  "status": "success",
  "customers": [
    {
      "customer_id": 1,
      "customer_name": "Maria Papadopoulou",
      "segment": "High Value Customers",
      "recency_days": 12,
      "frequency": 8,
      "monetary_value": 4200.00
    }
  ],
  "summary": [
    {
      "segment": "High Value Customers",
      "count": 25,
      "avg_monetary_value": 3800.00,
      "avg_frequency": 6.5,
      "avg_recency_days": 15.0
    }
  ]
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Resource Not Found |
| 422 | Validation Error (CSV import) |
| 500 | Internal Server Error |
