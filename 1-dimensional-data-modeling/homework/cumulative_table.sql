-- 2. Cumulative table generation query:
-- Write a query that populates the actors table one year at a time

-- Step 1: Get last year's actor data from the 'actors' table
WITH last_year_actors_data AS (
    SELECT * FROM actors
    WHERE active_year = 1974
),
-- Step 2: Aggregate current year's films per actor from 'actor_films'
this_year_actors_data AS (
    SELECT 
        actor,
        actorid,
        year,
        ARRAY_AGG(ROW(year, filmid, film, votes, rating)::film) AS current_year_films,
        AVG(rating) AS avg_rating
    FROM actor_films
    WHERE year = 1975
    GROUP BY actor, actorid, year
),
-- Step 3: Merge previous and current year data
combined_data AS (
    SELECT 
        COALESCE(curr.actor, prev.actor) AS actor,
        COALESCE(curr.actorid, prev.actorid) AS actorid,
        1975 AS active_year,
        CASE 
            WHEN prev.films is NULL THEN curr.current_year_films
            ELSE prev.films || curr.current_year_films
        END AS films,
        CASE 
            WHEN curr.avg_rating > 8 THEN 'star'
            WHEN curr.avg_rating > 7 THEN 'good'
            WHEN curr.avg_rating > 6 THEN 'average'
            WHEN curr.avg_rating IS NOT NULL THEN 'bad'
            ELSE prev.quality_class
        END::quality_class AS quality_class,
        CASE 
            WHEN curr.actorid IS NOT NULL THEN TRUE
            ELSE FALSE
        END AS is_active
    FROM this_year_actors_data curr
    FULL OUTER JOIN last_year_actors_data prev
    ON curr.actorid = prev.actorid
)

INSERT INTO actors
SELECT 
    actorid,
    actor,
    active_year,
    films,
    quality_class,
    is_active
FROM combined_data;  

