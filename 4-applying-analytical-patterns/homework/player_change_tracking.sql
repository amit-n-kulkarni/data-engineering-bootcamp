-- Query to track player state changes over seasons
-- States:
-- New: Player appears for the first time
-- Retired: Player leaves the league (appears previously, but not in current season)
-- Continued Playing: Player continues playing season over season
-- Returned from Retirement: Player appears again after one or more seasons out
-- Stayed Retired: Player does not play in current season and did not return

WITH player_activity AS (
    SELECT
        player_id,
        season,
        1 AS played
    FROM player_seasons
),
-- Generate all player-season pairs for the range of seasons in data
all_seasons AS (
    SELECT DISTINCT season FROM player_seasons
),
all_players AS (
    SELECT DISTINCT player_id FROM player_seasons
),
player_season_grid AS (
    SELECT
        p.player_id,
        s.season
    FROM all_players p
    CROSS JOIN all_seasons s
),
-- Left join to mark seasons where player played (played=1) or not (null)
player_activity_grid AS (
    SELECT
        g.player_id,
        g.season,
        COALESCE(a.played, 0) AS played
    FROM player_season_grid g
    LEFT JOIN player_activity a
        ON g.player_id = a.player_id AND g.season = a.season
),
-- Identify previous season activity
player_activity_lag AS (
    SELECT
        player_id,
        season,
        played,
        LAG(played) OVER (PARTITION BY player_id ORDER BY season) AS prev_played,
        -- Find gap between current season and previous season player played
        LAG(season) OVER (PARTITION BY player_id ORDER BY season) AS prev_season
    FROM player_activity_grid
),
-- Determine player state per season based on current and previous activity
player_state AS (
    SELECT
        player_id,
        season,
        played,
        prev_played,
        prev_season,
        CASE
            WHEN played = 1 AND prev_played IS NULL THEN 'New'                                  -- First time playing
            WHEN played = 0 AND prev_played = 1 THEN 'Retired'                                 -- Played previous, not current
            WHEN played = 1 AND prev_played = 1 THEN 'Continued Playing'                       -- Played previous and current
            WHEN played = 1 AND (prev_played = 0 OR (prev_played = 1 AND season - prev_season > 1)) THEN 'Returned from Retirement' -- Came back after missing seasons
            WHEN played = 0 AND prev_played = 0 THEN 'Stayed Retired'                          -- Did not play and was retired previous season
            ELSE 'Unknown'
        END AS player_state
    FROM player_activity_lag
)

SELECT * FROM player_state
ORDER BY player_id, season;
