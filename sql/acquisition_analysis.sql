-- Separates acquisition volume from downstream user value.
WITH user_value AS (
    SELECT
        u.user_id,
        u.acquisition_channel,
        DATE_TRUNC('month', u.signup_date) AS signup_month,
        COUNT(DISTINCT o.order_id) AS orders,
        COALESCE(SUM(o.order_value), 0) AS revenue
    FROM users u
    LEFT JOIN orders o USING (user_id)
    GROUP BY 1, 2, 3
)
SELECT
    signup_month,
    acquisition_channel,
    COUNT(*) AS acquired_users,
    COUNT_IF(orders > 0) AS purchasing_users,
    purchasing_users / acquired_users::DOUBLE AS purchase_rate,
    SUM(revenue) / acquired_users AS revenue_per_acquired_user
FROM user_value
GROUP BY 1, 2
ORDER BY 1, 2;

