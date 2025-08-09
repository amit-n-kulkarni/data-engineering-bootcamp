-- Using window functions on game_details

-- 1. Find the maximum number of games a team has won in any 90-game rolling window
WITH team_game_wins AS (
    SELECT
        team_id,
        game_date,
        CASE WHEN won = TRUE THEN 1 ELSE 0 END AS win_flag
    FROM game_details
),
team_wins_rolling AS (
    SELECT
        team_id,
        game_date,
        SUM(win_flag) OVER (
            PARTITION BY team_id
            ORDER BY game_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW  -- Last 90 games including current
        ) AS wins_in_90_games
    FROM team_game_wins
)
SELECT
    team_id,
    MAX(wins_in_90_games) AS max_wins_in_90_game_stretch
FROM team_wins_rolling
GROUP BY team_id
ORDER BY max_wins_in_90_game_stretch DESC;

-------------------------------------------------------------

-- 2. Calculate the longest streak of LeBron James scoring over 10 points in consecutive games

WITH lebron_games AS (
    SELECT
        game_id,
        game_date,
        points,
        CASE WHEN points > 10 THEN 1 ELSE 0 END AS over_10_points
    FROM game_details
    WHERE player_id = (SELECT player_id FROM players WHERE player_name = 'LeBron James' LIMIT 1)
    ORDER BY game_date
),
streaks AS (
    SELECT
        game_id,
        game_date,
        points,
        over_10_points,
        -- Identify streak groups where over_10_points=1
        SUM(CASE WHEN over_10_points = 0 THEN 1 ELSE 0 END) OVER (ORDER BY game_date ROWS UNBOUNDED PRECEDING) AS streak_group
    FROM lebron_games
)
SELECT
    MAX(COUNT(*)) AS longest_over_10_points_streak
FROM streaks
WHERE over_10_points = 1
GROUP BY streak_group;
