-- Early behavior is defined only from the first session to avoid future leakage.
WITH first_sessions AS (
    SELECT user_id, session_id
    FROM (
        SELECT user_id, session_id,
               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY MIN(event_timestamp)) AS rn
        FROM events GROUP BY 1, 2
    ) WHERE rn = 1
), early AS (
    SELECT f.user_id,
           COUNT_IF(e.event_name = 'offer_view') >= 2 AS compared_two_offers
    FROM first_sessions f JOIN events e USING (user_id, session_id)
    GROUP BY 1
), outcome AS (
    SELECT user_id, COUNT(*) > 0 AS purchased FROM orders GROUP BY 1
)
SELECT
    compared_two_offers,
    COUNT(*) AS users,
    COUNT_IF(COALESCE(purchased, FALSE)) AS purchasing_users,
    purchasing_users / users::DOUBLE AS purchase_rate
FROM early LEFT JOIN outcome USING (user_id)
GROUP BY 1;

