-- Repeat purchase within 60 days, restricted to first orders with a full follow-up window.
WITH ranked AS (
    SELECT user_id, order_timestamp,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_timestamp) AS order_number,
           LEAD(order_timestamp) OVER (PARTITION BY user_id ORDER BY order_timestamp) AS next_order_at
    FROM orders
), eligible AS (
    SELECT r.*, u.acquisition_channel
    FROM ranked r JOIN users u USING (user_id)
    WHERE order_number = 1 AND order_timestamp <= TIMESTAMP '2024-05-01'
)
SELECT
    acquisition_channel,
    COUNT(*) AS first_time_buyers,
    COUNT_IF(next_order_at <= order_timestamp + INTERVAL '60 days') AS repeat_buyers_60d,
    repeat_buyers_60d / first_time_buyers::DOUBLE AS repeat_purchase_rate_60d
FROM eligible
GROUP BY 1
ORDER BY 1;

