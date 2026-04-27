SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(quantity * unit_price) AS monthly_revenue,
    COUNT(DISTINCT order_id) AS orders,
    AVG(quantity * unit_price) AS average_order_value
FROM sales
GROUP BY 1
ORDER BY 1;

SELECT
    region,
    SUM(quantity * unit_price) AS revenue,
    SUM(quantity) AS units_sold
FROM sales
GROUP BY region
ORDER BY revenue DESC;

SELECT
    category,
    SUM(quantity * unit_price) AS revenue
FROM sales
GROUP BY category
ORDER BY revenue DESC;
