-- Monthly Sales Summary
SELECT 
    TO_CHAR(o.order_date, 'YYYY-MM') AS month,
    SUM(o.total_amount) AS revenue,
    SUM(oi.line_total - (oi.quantity * p.cost_price)) AS profit,
    COUNT(DISTINCT o.id) AS orders
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
GROUP BY month
ORDER BY month;

-- Top Products by Revenue
SELECT 
    p.id AS product_id,
    p.name AS product_name,
    p.category,
    SUM(oi.quantity) AS quantity_sold,
    SUM(oi.line_total) AS revenue,
    SUM(oi.line_total - (oi.quantity * p.cost_price)) AS profit
FROM products p
JOIN order_items oi ON oi.product_id = p.id
JOIN orders o ON o.id = oi.order_id
GROUP BY p.id, p.name, p.category
ORDER BY revenue DESC
LIMIT 10;

-- Top Customers by Total Spent
SELECT 
    c.id AS customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.country,
    COUNT(DISTINCT o.id) AS orders,
    SUM(o.total_amount) AS total_spent,
    AVG(o.total_amount) AS average_order_value
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.first_name, c.last_name, c.country
ORDER BY total_spent DESC
LIMIT 10;

-- Sales by Country
SELECT 
    o.country,
    SUM(o.total_amount) AS revenue,
    COUNT(DISTINCT o.id) AS orders,
    COUNT(DISTINCT c.id) AS customers
FROM orders o
JOIN customers c ON c.id = o.customer_id
GROUP BY o.country
ORDER BY revenue DESC;

-- Average Order Value
SELECT 
    AVG(total_amount) AS overall_aov,
    MIN(total_amount) AS min_order,
    MAX(total_amount) AS max_order
FROM orders;

-- Profit by Category
SELECT 
    p.category,
    SUM(oi.line_total) AS revenue,
    SUM(oi.quantity * p.cost_price) AS total_cost,
    SUM(oi.line_total - (oi.quantity * p.cost_price)) AS profit
FROM products p
JOIN order_items oi ON oi.product_id = p.id
GROUP BY p.category
ORDER BY profit DESC;

-- Payment Status Summary
SELECT 
    payment_status,
    SUM(paid_amount) AS total_amount,
    COUNT(*) AS count
FROM payments
GROUP BY payment_status;

-- Customer RFM Features (Recency, Frequency, Monetary)
SELECT 
    c.id AS customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    CURRENT_DATE - MAX(o.order_date) AS recency_days,
    COUNT(DISTINCT o.id) AS frequency,
    SUM(o.total_amount) AS monetary_value,
    AVG(o.total_amount) AS average_order_value
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.first_name, c.last_name;
