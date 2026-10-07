-- Products with the highest return rate (returned value / sales value).
-- Only products with at least 5,000 in sales, so tiny products do not dominate the list.
WITH sold AS (
    SELECT stock_code, MAX(description) AS description, SUM(revenue) AS sales_value
    FROM sales
    GROUP BY stock_code
    HAVING SUM(revenue) >= 5000
),
returned AS (
    SELECT stock_code, SUM(revenue) AS return_value
    FROM returns
    GROUP BY stock_code
)
SELECT sold.stock_code,
       sold.description,
       ROUND(sold.sales_value, 2)                                       AS sales_value,
       ROUND(COALESCE(returned.return_value, 0), 2)                     AS return_value,
       ROUND(100.0 * COALESCE(returned.return_value, 0) / sold.sales_value, 1) AS return_rate_pct
FROM sold
LEFT JOIN returned USING (stock_code)
ORDER BY return_rate_pct DESC
LIMIT 10;
