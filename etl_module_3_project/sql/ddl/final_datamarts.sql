-- Final Project: Analytical Data Marts (materialized views in mart schema)

-- =============================================
-- dm_user_activity
-- =============================================
DROP MATERIALIZED VIEW IF EXISTS mart.dm_user_activity;

CREATE MATERIALIZED VIEW mart.dm_user_activity AS
WITH session_stats AS (
    SELECT
        s.user_id,
        COUNT(DISTINCT s.session_id)                            AS total_sessions,
        SUM(EXTRACT(EPOCH FROM (s.end_time - s.start_time)))    AS total_time_seconds,
        AVG(EXTRACT(EPOCH FROM (s.end_time - s.start_time)))    AS avg_time_seconds
    FROM dwh.sessions s
    WHERE s.end_time IS NOT NULL
    GROUP BY s.user_id
),
popular_pages AS (
    SELECT
        s.user_id,
        sp.page_url,
        COUNT(*)                                                AS visit_count,
        ROW_NUMBER() OVER (PARTITION BY s.user_id ORDER BY COUNT(*) DESC) AS rn
    FROM dwh.sessions s
    JOIN dwh.session_pages sp ON s.session_id = sp.session_id
    GROUP BY s.user_id, sp.page_url
),
popular_actions AS (
    SELECT
        s.user_id,
        sa.action_name,
        COUNT(*)                                                AS action_count,
        ROW_NUMBER() OVER (PARTITION BY s.user_id ORDER BY COUNT(*) DESC) AS rn
    FROM dwh.sessions s
    JOIN dwh.session_actions sa ON s.session_id = sa.session_id
    GROUP BY s.user_id, sa.action_name
),
daily_activity AS (
    SELECT
        s.user_id,
        s.start_time::date                                      AS activity_date,
        EXTRACT(DOW FROM s.start_time)                          AS day_of_week,
        EXTRACT(HOUR FROM s.start_time)                         AS hour_of_day,
        COUNT(DISTINCT s.session_id)                            AS sessions_count
    FROM dwh.sessions s
    GROUP BY s.user_id, s.start_time::date,
             EXTRACT(DOW FROM s.start_time),
             EXTRACT(HOUR FROM s.start_time)
)
SELECT
    ss.user_id,
    ss.total_sessions,
    ROUND(ss.total_time_seconds)                                AS total_time_seconds,
    ROUND(ss.avg_time_seconds)                                  AS avg_time_seconds,
    pp.page_url                                                 AS top_page,
    pa.action_name                                              AS top_action,
    da.activity_date,
    da.day_of_week,
    da.hour_of_day,
    da.sessions_count                                           AS daily_sessions
FROM session_stats ss
LEFT JOIN popular_pages pp   ON ss.user_id = pp.user_id AND pp.rn = 1
LEFT JOIN popular_actions pa ON ss.user_id = pa.user_id AND pa.rn = 1
LEFT JOIN daily_activity da  ON ss.user_id = da.user_id;

CREATE INDEX IF NOT EXISTS idx_dm_user_activity_user ON mart.dm_user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_dm_user_activity_date ON mart.dm_user_activity(activity_date);


-- =============================================
-- dm_support_efficiency
-- =============================================
DROP MATERIALIZED VIEW IF EXISTS mart.dm_support_efficiency;

CREATE MATERIALIZED VIEW mart.dm_support_efficiency AS
WITH ticket_aggs AS (
    SELECT
        t.status,
        t.issue_type,
        COUNT(*)                                                            AS ticket_count,
        AVG(EXTRACT(EPOCH FROM (t.updated_at - t.created_at)) / 3600.0)    AS avg_resolution_hours
    FROM dwh.tickets t
    GROUP BY t.status, t.issue_type
),
open_tickets AS (
    SELECT COUNT(*) AS open_count
    FROM dwh.tickets
    WHERE status = 'open'
),
daily_tickets AS (
    SELECT
        t.created_at::date                                      AS ticket_date,
        t.status,
        t.issue_type,
        COUNT(*)                                                AS daily_count
    FROM dwh.tickets t
    GROUP BY t.created_at::date, t.status, t.issue_type
),
weekly_tickets AS (
    SELECT
        DATE_TRUNC('week', t.created_at)::date                  AS week_start,
        t.status,
        t.issue_type,
        COUNT(*)                                                AS weekly_count
    FROM dwh.tickets t
    GROUP BY DATE_TRUNC('week', t.created_at), t.status, t.issue_type
)
SELECT
    ta.status,
    ta.issue_type,
    ta.ticket_count,
    ROUND(ta.avg_resolution_hours::numeric, 2)                  AS avg_resolution_hours,
    ot.open_count                                               AS total_open_tickets,
    dt.ticket_date,
    dt.daily_count,
    wt.week_start,
    wt.weekly_count
FROM ticket_aggs ta
CROSS JOIN open_tickets ot
LEFT JOIN daily_tickets dt  ON ta.status = dt.status AND ta.issue_type = dt.issue_type
LEFT JOIN weekly_tickets wt ON ta.status = wt.status AND ta.issue_type = wt.issue_type;

CREATE INDEX IF NOT EXISTS idx_dm_support_status ON mart.dm_support_efficiency(status);
CREATE INDEX IF NOT EXISTS idx_dm_support_date   ON mart.dm_support_efficiency(ticket_date);
