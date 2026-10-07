-- When do customers buy? Revenue by weekday and hour (SQLite strftime: %w is 0 = Sunday).
SELECT CASE strftime('%w', invoice_date)
           WHEN '0' THEN 'Sun' WHEN '1' THEN 'Mon' WHEN '2' THEN 'Tue' WHEN '3' THEN 'Wed'
           WHEN '4' THEN 'Thu' WHEN '5' THEN 'Fri' ELSE 'Sat' END AS weekday,
       CAST(strftime('%w', invoice_date) AS INTEGER)              AS weekday_num,
       CAST(strftime('%H', invoice_date) AS INTEGER)              AS hour,
       ROUND(SUM(revenue), 2)                                     AS revenue,
       COUNT(DISTINCT invoice_no)                                 AS orders
FROM sales
GROUP BY weekday_num, hour
ORDER BY weekday_num, hour;
