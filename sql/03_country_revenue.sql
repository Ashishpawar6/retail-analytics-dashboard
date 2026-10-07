-- Revenue by country with share of total. SUM(...) OVER () is the grand total on every row.
SELECT country,
       ROUND(SUM(revenue), 2)                                        AS revenue,
       COUNT(DISTINCT invoice_no)                                    AS orders,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 2)    AS revenue_share_pct
FROM sales
GROUP BY country
ORDER BY revenue DESC;
