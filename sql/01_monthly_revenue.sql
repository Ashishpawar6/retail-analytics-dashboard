-- Monthly revenue, orders, customers and average order value, with month-over-month growth.
-- LAG() looks at the previous month's row so growth needs no self-join.
-- Note: December 2011 only covers 1-9 Dec, so its growth figure is not comparable.
WITH monthly AS (
    SELECT invoice_month                    AS month,
           SUM(revenue)                     AS revenue,
           COUNT(DISTINCT invoice_no)       AS orders,
           COUNT(DISTINCT customer_id)      AS customers
    FROM sales
    GROUP BY invoice_month
)
SELECT month,
       ROUND(revenue, 2)                                   AS revenue,
       orders,
       customers,
       ROUND(revenue * 1.0 / orders, 2)                    AS avg_order_value,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1)      AS mom_growth_pct
FROM monthly
ORDER BY month;
