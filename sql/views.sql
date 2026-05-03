-- View: Monthly Revenue Overview
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT 
    TO_CHAR(o.order_date, 'YYYY-MM') AS month,
    SUM(o.total_amount) AS revenue,
    SUM(oi.line_total - (oi.quantity * p.cost_price)) AS profit,
    COUNT(DISTINCT o.id) AS orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
GROUP BY month
ORDER BY month;

-- View: Customer Lifetime Value Summary
CREATE OR REPLACE VIEW v_customer_ltv AS
SELECT 
    c.id AS customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.country,
    COUNT(DISTINCT o.id) AS total_orders,
    SUM(o.total_amount) AS lifetime_value,
    AVG(o.total_amount) AS avg_order_value,
    MAX(o.order_date) AS last_order_date,
    CURRENT_DATE - MAX(o.order_date) AS days_since_last_order
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.first_name, c.last_name, c.country;

-- View: Product Performance
CREATE OR REPLACE VIEW v_product_performance AS
SELECT 
    p.id AS product_id,
    p.product_code,
    p.name AS product_name,
    p.category,
    COUNT(DISTINCT oi.order_id) AS orders_with_product,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.line_total) AS total_revenue,
    SUM(oi.line_total - (oi.quantity * p.cost_price)) AS total_profit,
    AVG(oi.unit_price) AS avg_selling_price
FROM products p
JOIN order_items oi ON oi.product_id = p.id
GROUP BY p.id, p.product_code, p.name, p.category;
