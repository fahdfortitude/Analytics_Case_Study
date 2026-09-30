-- First-session offer depth predicts only purchases after that session, within
-- a complete 14-day observation window. Same-session purchases do not qualify.
WITH session_bounds AS (
    SELECT user_id, session_id, MIN(event_timestamp) AS session_start,
           MAX(event_timestamp) AS session_end
    FROM events GROUP BY 1, 2
), first_sessions AS (
    SELECT user_id, session_id, session_start, session_end
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY session_start) AS rn
        FROM session_bounds
    ) WHERE rn = 1
), early AS (
    SELECT f.user_id, f.session_start, f.session_end,
           CASE WHEN COUNT_IF(e.event_name = 'offer_view') = 0 THEN '0'
                WHEN COUNT_IF(e.event_name = 'offer_view') = 1 THEN '1'
                WHEN COUNT_IF(e.event_name = 'offer_view') = 2 THEN '2'
                ELSE '3+' END AS offer_depth_group
    FROM first_sessions f JOIN events e USING (user_id, session_id)
    GROUP BY 1, 2, 3
), outcome AS (
    SELECT e.user_id, e.offer_depth_group,
           COUNT(o.order_id) > 0 AS subsequent_purchase_14d
    FROM early e LEFT JOIN orders o
      ON e.user_id = o.user_id
     AND o.order_timestamp > e.session_end
     AND o.order_timestamp <= e.session_start + INTERVAL '14 days'
    WHERE e.session_start <= (SELECT MAX(event_timestamp) FROM events) - INTERVAL '14 days'
    GROUP BY 1, 2
)
SELECT
    offer_depth_group,
    COUNT(*) AS users,
    COUNT_IF(subsequent_purchase_14d) AS subsequent_purchasers_14d,
    subsequent_purchasers_14d / users::DOUBLE AS subsequent_purchase_rate_14d
FROM outcome
GROUP BY 1;

