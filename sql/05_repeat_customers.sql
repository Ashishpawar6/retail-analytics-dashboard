-- What share of known customers ordered more than once?
WITH orders_per_customer AS (
    SELECT customer_id, COUNT(DISTINCT invoice_no) AS orders
    FROM sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT COUNT(*)                                    AS customers,
       SUM(orders > 1)                             AS repeat_customers,
       ROUND(100.0 * SUM(orders > 1) / COUNT(*), 1) AS repeat_rate_pct,
       ROUND(AVG(orders), 1)                       AS avg_orders_per_customer
FROM orders_per_customer;
