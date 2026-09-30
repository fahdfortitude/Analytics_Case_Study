-- Time-to-first-purchase among converters; non-converters remain outside this conditional metric.
WITH first_orders AS (
    SELECT user_id, MIN(order_timestamp) AS first_order_at
    FROM orders GROUP BY 1
)
SELECT
    u.acquisition_channel,
    COUNT(*) AS purchasers,
    MEDIAN(DATE_DIFF('hour', u.signup_date, f.first_order_at)) / 24.0 AS median_days_to_first_purchase,
    QUANTILE_CONT(DATE_DIFF('hour', u.signup_date, f.first_order_at) / 24.0, 0.75) AS p75_days_to_first_purchase
FROM users u
JOIN first_orders f USING (user_id)
GROUP BY 1
ORDER BY purchasers DESC;

