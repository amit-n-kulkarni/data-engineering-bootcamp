-- Step 1: Detect changes in actor attributes (is_active or quality_class) over time
WITH change_identifier AS (
    SELECT
        actorid,
        actor,
        quality_class,
        is_active,
        active_year,
        CASE 
            WHEN is_active <> LAG(is_active, 1) OVER (PARTITION BY actorid ORDER BY active_year)
              OR quality_class <> LAG(quality_class, 1) OVER (PARTITION BY actorid ORDER BY active_year)
            THEN 1 
            ELSE 0 
        END AS change_indicator
    FROM actors
    WHERE active_year < 2021  
),

-- Step 2: Assign a group number to each continuous segment of unchanged attributes
cte2 AS (
    SELECT *,
        SUM(change_indicator) OVER (PARTITION BY actorid ORDER BY active_year) AS change_group
    FROM change_identifier
)

INSERT INTO actors_history_scd
SELECT 
    actorid,
    actor,
    quality_class,
    is_active,
    MIN(active_year) AS start_date,         
    MAX(active_year) + 1 AS end_date       
FROM cte2
GROUP BY 
    actorid,
    actor,
    is_active,
    quality_class,
    change_group                           
ORDER BY 
    actorid,
    change_group;