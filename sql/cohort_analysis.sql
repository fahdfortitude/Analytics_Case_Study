-- Maturity-aware acquisition cohorts: conversion within 30 days of signup.
SELECT
    DATE_TRUNC('month', u.signup_date) AS signup_month,
    COUNT(*) AS acquired_users,
    COUNT_IF(o.first_order_at <= u.signup_date + INTERVAL '30 days') AS purchasers_30d,
    purchasers_30d / acquired_users::DOUBLE AS purchase_rate_30d
FROM users u
LEFT JOIN (
    SELECT user_id, MIN(order_timestamp) AS first_order_at
    FROM orders GROUP BY 1
) o USING (user_id)
WHERE u.signup_date <= TIMESTAMP '2024-05-31 23:59:59'
GROUP BY 1
ORDER BY 1;

