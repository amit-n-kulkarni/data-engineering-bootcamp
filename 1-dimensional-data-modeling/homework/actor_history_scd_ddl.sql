-- 2. DDL for actors_history_scd table:
-- Implements type 2 dimension modeling (i.e., includes start_date and end_date fields).
-- Tracks quality_class and is_active status for each actor in the actors table.


DROP TABLE IF EXISTS actors_history_scd;

CREATE TABLE actors_history_scd (
    actorid text,
    actor text,
    quality_class quality_class,
    is_active boolean,
    start_date integer,
    end_date integer,
    PRIMARY KEY (actorid, start_date)
);
