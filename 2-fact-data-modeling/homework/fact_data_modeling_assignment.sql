-- Homework: Devices & Events Dataset Queries

-- =================================================================
-- 1. Deduplicate game_details from Day 1 so there's no duplicates
-- =================================================================
WITH ranked AS (
    SELECT
        gd.*,
        ROW_NUMBER() OVER (PARTITION BY game_id, player_id, team_id ORDER BY updated_at DESC) AS rn
    FROM game_details gd
)
SELECT *
FROM ranked
WHERE rn = 1;
-- Deduplication uses ROW_NUMBER to keep the latest record per game_id/player_id combination

-- ===================================================================
-- 2. DDL for user_devices_cumulated table
--    - Includes a complex MAP<STRING, ARRAY<DATE>> column to store active days per browser
-- ===================================================================
CREATE TABLE user_devices_cumulated (
    user_id BIGINT,
    device_activity_datelist MAP<STRING, ARRAY<DATE>>,
    updated_at TIMESTAMP
);
-- The MAP<STRING, ARRAY<DATE>> datatype maps browser_type -> array of active dates.
-- This structure allows flexible expansion for new browser types without schema changes.

-- ===================================================================
-- 3. Cumulative query to generate device_activity_datelist from events
-- ===================================================================
WITH user_browser_dates AS (
    SELECT user_id,
           browser_type,
           COLLECT_SET(event_date) AS active_dates
    FROM events
    GROUP BY user_id, browser_type
),
device_map AS (
    SELECT user_id,
           MAP_FROM_ENTRIES(COLLECT_LIST(NAMED_STRUCT('key', browser_type, 'value', active_dates))) AS device_activity_datelist
    FROM user_browser_dates
    GROUP BY user_id
)
INSERT INTO user_devices_cumulated
SELECT user_id, device_activity_datelist, CURRENT_TIMESTAMP()
FROM device_map;
-- COLLECT_SET ensures each date is unique.
-- MAP_FROM_ENTRIES constructs the required map structure of browser -> dates.

-- ===================================================================
-- 4. Query to convert device_activity_datelist into datelist_int
-- ===================================================================
-- For bit-encoding dates (e.g. days in a month) into an integer flag.
-- Each bit represents activity on a specific day.

CREATE TABLE user_devices_datelist_int AS
SELECT user_id,
       TRANSFORM_VALUES(device_activity_datelist, (dates -> REDUCE(dates, 0, (acc, d) -> acc + CAST(POW(2, DAY(d) - 1) AS INT))) ) AS datelist_int_map
FROM user_devices_cumulated;
-- TRANSFORM_VALUES applies a function to each array of dates, producing a compact integer.
-- POW(2, DAY(d)-1) encodes each day of the month as a distinct bit.

-- ===================================================================
-- 5. DDL for hosts_cumulated table
-- ===================================================================
CREATE TABLE hosts_cumulated (
    host STRING,
    host_activity_datelist ARRAY<DATE>,
    updated_at TIMESTAMP
);
-- ARRAY<DATE> is chosen to store a simple ordered list of activity dates per host.

-- ===================================================================
-- 6. Incremental query to generate host_activity_datelist
-- ===================================================================
WITH host_dates AS (
    SELECT host,
           COLLECT_SET(event_date) AS active_dates
    FROM events
    GROUP BY host
)
INSERT INTO hosts_cumulated
SELECT host, active_dates, CURRENT_TIMESTAMP()
FROM host_dates;
-- COLLECT_SET ensures no duplicate dates; incremental loads append/merge new days.

-- ===================================================================
-- 7. DDL for monthly reduced fact table host_activity_reduced
-- ===================================================================
CREATE TABLE host_activity_reduced (
    month DATE,
    host STRING,
    hit_array ARRAY<INT>,
    unique_visitors ARRAY<INT>,
    updated_at TIMESTAMP
);
-- hit_array holds daily hit counts for the month.
-- unique_visitors stores daily distinct user counts.
-- ARRAY is used to align daily metrics by day-of-month index.

-- ===================================================================
-- 8. Incremental query to load host_activity_reduced day-by-day
-- ===================================================================
WITH daily_stats AS (
    SELECT DATE_TRUNC('month', event_date) AS month,
           host,
           DAY(event_date) AS day_idx,
           COUNT(1) AS hits,
           COUNT(DISTINCT user_id) AS visitors
    FROM events
    GROUP BY DATE_TRUNC('month', event_date), host, DAY(event_date)
),
aggregated AS (
    SELECT month,
           host,
           COLLECT_LIST(hits) AS hit_array,
           COLLECT_LIST(visitors) AS unique_visitors
    FROM daily_stats
    GROUP BY month, host
)
INSERT INTO host_activity_reduced
SELECT month, host, hit_array, unique_visitors, CURRENT_TIMESTAMP()
FROM aggregated;
-- COLLECT_LIST creates arrays ordered by day index (assuming prior ordering).
-- This query supports incremental loading by re-running for new days and merging with existing arrays.
