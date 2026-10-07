-- Top 10 products by NET revenue (sales minus returns).
-- Ranking by gross revenue would be misleading: some large orders are cancelled in full
-- (for example product 23843, an 80,995-unit order that was cancelled), so gross and net differ a lot.
WITH sold AS (
    SELECT stock_code, MAX(description) AS description, SUM(quantity) AS units, SUM(revenue) AS gross_revenue
    FROM sales
    GROUP BY stock_code
),
returned AS (
    SELECT stock_code, SUM(revenue) AS return_value
    FROM returns
    GROUP BY stock_code
)
SELECT sold.stock_code,
       sold.description,
       sold.units,
       ROUND(sold.gross_revenue, 2)                                              AS gross_revenue,
       ROUND(COALESCE(returned.return_value, 0), 2)                              AS return_value,
       ROUND(sold.gross_revenue - COALESCE(returned.return_value, 0), 2)         AS net_revenue,
       ROUND(100.0 * (sold.gross_revenue - COALESCE(returned.return_value, 0))
             / ((SELECT SUM(revenue) FROM sales) - (SELECT COALESCE(SUM(revenue), 0) FROM returns)), 2)
                                                                                 AS net_revenue_share_pct
FROM sold
LEFT JOIN returned USING (stock_code)
ORDER BY net_revenue DESC
LIMIT 10;
