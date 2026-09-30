-- User-level marketplace funnel; denominators are all acquired users.
WITH user_steps AS (
    SELECT
        u.user_id,
        MAX((e.event_name = 'session_start')::INT) AS reached_session,
        MAX((e.event_name = 'listing_view')::INT) AS reached_listing,
        MAX((e.event_name = 'offer_view')::INT) AS reached_offer,
        MAX((e.event_name = 'checkout_start')::INT) AS reached_checkout,
        MAX((e.event_name = 'purchase')::INT) AS reached_purchase
    FROM users u
    LEFT JOIN events e USING (user_id)
    GROUP BY 1
)
SELECT
    COUNT(*) AS acquired_users,
    SUM(reached_session) AS session_users,
    SUM(reached_listing) AS listing_users,
    SUM(reached_offer) AS offer_users,
    SUM(reached_checkout) AS checkout_users,
    SUM(reached_purchase) AS purchasing_users,
    purchasing_users / acquired_users::DOUBLE AS user_purchase_rate,
    purchasing_users / NULLIF(checkout_users, 0)::DOUBLE AS checkout_completion_rate
FROM user_steps;

