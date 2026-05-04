-- ============================================
-- Sales Analysis Queries
-- ============================================
-- These are the SQL equivalents of what the Python dashboard does.
-- I wrote them to practice translating between Pandas and SQL since
-- both are used heavily in data roles.
--
-- Assumes a table called 'sales' with columns:
--   order_id, order_date, region, category, product, quantity, unit_price
-- ============================================


-- 1) Monthly Revenue Summary
-- DATE_TRUNC groups all dates in the same month together.
-- COUNT(DISTINCT order_id) gives unique orders, not just row count,
-- because one order can have multiple products.
SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(quantity * unit_price)      AS monthly_revenue,
    COUNT(DISTINCT order_id)        AS total_orders,
    AVG(quantity * unit_price)      AS avg_line_value
FROM sales
GROUP BY 1
ORDER BY 1;


-- 2) Revenue by Region
-- This is the data behind the bar chart in the dashboard.
-- ORDER BY revenue DESC so the highest performing region shows first.
SELECT
    region,
    SUM(quantity * unit_price) AS revenue,
    SUM(quantity)              AS units_sold
FROM sales
GROUP BY region
ORDER BY revenue DESC;


-- 3) Revenue by Category
-- Same idea as region but sliced by product category.
-- Maps to the pie chart in the dashboard.
SELECT
    category,
    SUM(quantity * unit_price) AS revenue,
    COUNT(DISTINCT order_id)   AS total_orders
FROM sales
GROUP BY category
ORDER BY revenue DESC;


-- 4) Top 10 Products by Revenue
-- LIMIT 10 is the SQL version of .head(10) in Pandas.
SELECT
    product,
    SUM(quantity * unit_price) AS revenue,
    SUM(quantity)              AS total_quantity_sold
FROM sales
GROUP BY product
ORDER BY revenue DESC
LIMIT 10;
