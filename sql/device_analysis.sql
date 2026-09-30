-- Checkout completion isolates post-checkout friction from upstream intent.
WITH session_steps AS (
    SELECT
        session_id,
        ANY_VALUE(device_type) AS device_type,
        MAX((event_name = 'checkout_start')::INT) AS checkout_started,
        MAX((event_name = 'purchase')::INT) AS purchased
    FROM events
    GROUP BY 1
)
SELECT
    device_type,
    COUNT_IF(checkout_started = 1) AS checkout_sessions,
    COUNT_IF(purchased = 1) AS purchase_sessions,
    purchase_sessions / checkout_sessions::DOUBLE AS checkout_completion_rate
FROM session_steps
GROUP BY 1;

