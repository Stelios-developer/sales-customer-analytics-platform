# Data Dictionary

## customers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer | PK | Auto-increment primary key |
| customer_code | varchar(50) | UNIQUE, NOT NULL | External customer identifier |
| first_name | varchar(100) | NOT NULL | Customer first name |
| last_name | varchar(100) | NOT NULL | Customer last name |
| email | varchar(255) | | Contact email |
| country | varchar(100) | NOT NULL, INDEX | Country of residence |
| city | varchar(100) | NOT NULL, DEFAULT 'Unknown' | City of residence |
| segment | varchar(100) | | ML-derived segment label |
| created_at | timestamp | DEFAULT now() | Record creation time |
| updated_at | timestamp | DEFAULT now() | Last update time |

## products

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer | PK | Auto-increment primary key |
| product_code | varchar(50) | UNIQUE, NOT NULL | External product identifier |
| name | varchar(255) | NOT NULL | Product name |
| category | varchar(100) | NOT NULL, INDEX | Product category |
| unit_price | numeric(12,2) | NOT NULL | Selling price |
| cost_price | numeric(12,2) | NOT NULL | Cost price for profit calc |
| created_at | timestamp | DEFAULT now() | Record creation time |
| updated_at | timestamp | DEFAULT now() | Last update time |

## orders

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer | PK | Auto-increment primary key |
| order_number | varchar(50) | UNIQUE, NOT NULL | External order identifier |
| customer_id | integer | FK -> customers.id, CASCADE | Customer who placed order |
| order_date | date | NOT NULL, INDEX | Date of order |
| status | varchar(50) | NOT NULL, DEFAULT 'completed' | Order status |
| total_amount | numeric(12,2) | NOT NULL | Order total including shipping |
| discount_amount | numeric(12,2) | NOT NULL, DEFAULT 0 | Total discount |
| shipping_amount | numeric(12,2) | NOT NULL, DEFAULT 0 | Shipping cost |
| country | varchar(100) | NOT NULL, INDEX | Shipping country |
| city | varchar(100) | NOT NULL, DEFAULT 'Unknown' | Shipping city |
| created_at | timestamp | DEFAULT now() | Record creation time |
| updated_at | timestamp | DEFAULT now() | Last update time |

## order_items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer | PK | Auto-increment primary key |
| order_id | integer | FK -> orders.id, CASCADE | Parent order |
| product_id | integer | FK -> products.id, RESTRICT | Product sold |
| quantity | integer | NOT NULL | Quantity sold |
| unit_price | numeric(12,2) | NOT NULL | Price at time of sale |
| discount_amount | numeric(12,2) | NOT NULL, DEFAULT 0 | Line-level discount |
| line_total | numeric(12,2) | NOT NULL | quantity * unit_price - discount |
| created_at | timestamp | DEFAULT now() | Record creation time |
| updated_at | timestamp | DEFAULT now() | Last update time |

## payments

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer | PK | Auto-increment primary key |
| order_id | integer | FK -> orders.id, CASCADE, UNIQUE | Associated order |
| payment_method | varchar(50) | NOT NULL, INDEX | Method (Credit Card, PayPal, etc.) |
| payment_status | varchar(50) | NOT NULL, DEFAULT 'pending', INDEX | paid / pending / failed |
| paid_amount | numeric(12,2) | NOT NULL, DEFAULT 0 | Amount paid |
| payment_date | date | | Date of payment |
| created_at | timestamp | DEFAULT now() | Record creation time |

## data_import_logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer | PK | Auto-increment primary key |
| filename | varchar(255) | NOT NULL | Uploaded file name |
| rows_processed | integer | NOT NULL, DEFAULT 0 | Rows read from CSV |
| rows_inserted | integer | NOT NULL, DEFAULT 0 | Rows successfully inserted |
| rows_failed | integer | NOT NULL, DEFAULT 0 | Rows that failed validation |
| status | varchar(50) | NOT NULL, DEFAULT 'pending' | success / partial / failed |
| error_message | text | | Error details if failed |
| created_at | timestamp | DEFAULT now() | Record creation time |

## ml_model_runs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer | PK | Auto-increment primary key |
| model_type | varchar(50) | NOT NULL, INDEX | forecasting / segmentation |
| model_name | varchar(100) | NOT NULL | Algorithm used |
| metrics_json | text | | JSON string of evaluation metrics |
| artifact_path | varchar(255) | | File path to saved model |
| created_at | timestamp | DEFAULT now() | Record creation time |
