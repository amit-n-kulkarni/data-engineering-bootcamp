-- Aggregation query using GROUPING SETS on game_details
-- Dimensions: player & team, player & season, team

SELECT
    player_id,
    team_id,
    season,
    SUM(points) AS total_points,
    SUM(CASE WHEN won = TRUE THEN 1 ELSE 0 END) AS total_wins
FROM game_details
GROUP BY GROUPING SETS (
    (player_id, team_id),    -- Who scored most points playing for a team
    (player_id, season),     -- Who scored most points in a season
    (team_id)                -- Which team has won the most games
)
ORDER BY
    -- Sorting logic to group aggregates by dimension combinations
    CASE 
        WHEN player_id IS NOT NULL AND team_id IS NOT NULL THEN 1
        WHEN player_id IS NOT NULL AND season IS NOT NULL THEN 2
        WHEN player_id IS NULL AND team_id IS NOT NULL THEN 3
        ELSE 4
    END,
    total_points DESC,
    total_wins DESC;
