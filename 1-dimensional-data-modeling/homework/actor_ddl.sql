-- 1. DDL (Data Definition Language) for actors table:

DROP TYPE IF EXISTS film;

CREATE TYPE film AS (
    year integer,
	filmid text,
	film text,
	votes integer,
	rating real
);


DROP TYPE IF EXISTS quality_class;

CREATE TYPE quality_class AS ENUM ('star', 'good', 'average', 'bad');


DROP TABLE IF EXISTS actors;

CREATE TABLE actors (
    actorid text,
    actor text,
    active_year integer,
    films film[],
    quality_class quality_class,
    is_active boolean,
    PRIMARY KEY (actorid, active_year)
);