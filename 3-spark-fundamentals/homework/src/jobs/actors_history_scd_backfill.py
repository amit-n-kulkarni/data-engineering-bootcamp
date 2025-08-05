from pyspark.sql import SparkSession

def backfill_actors_history_scd(actors_path, history_path, output_path):
    spark = SparkSession.builder.appName("ActorsHistorySCDBackfill").getOrCreate()

    # Load current and history data
    actors = spark.read.parquet(actors_path)
    history = spark.read.parquet(history_path)

    actors.createOrReplaceTempView("actors")
    history.createOrReplaceTempView("actors_history_scd")

    # Backfill SCD
    backfilled = spark.sql("""
        SELECT a.actor_id, a.actor_name, CURRENT_DATE() AS start_date, NULL AS end_date
        FROM actors a
        LEFT JOIN actors_history_scd h
        ON a.actor_id = h.actor_id
        WHERE h.actor_id IS NULL
    """)

    backfilled.write.mode("overwrite").parquet(output_path)
    spark.stop()
