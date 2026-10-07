-- How concentrated is revenue? Customers are split into 10 equal groups (deciles) by spend;
-- decile 1 is the top 10% of customers. Only customers with an ID are included.
WITH customer_revenue AS (
    SELECT customer_id, SUM(revenue) AS revenue
    FROM sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
ranked AS (
    SELECT customer_id, revenue, NTILE(10) OVER (ORDER BY revenue DESC) AS decile
    FROM customer_revenue
)
SELECT decile,
       COUNT(*)                                                       AS customers,
       ROUND(SUM(revenue), 2)                                         AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1)     AS revenue_share_pct
FROM ranked
GROUP BY decile
ORDER BY decile;
