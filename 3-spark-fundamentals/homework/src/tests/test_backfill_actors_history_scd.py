import pytest
from pyspark.sql import SparkSession
from ..jobs.top_playlist import most_played_playlist

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[2]").appName("TestTopPlaylist").getOrCreate()


def test_backfill_actors_history_scd(spark, tmp_path):
    actors = spark.createDataFrame([("a1", "Actor One")], ["actor_id", "actor_name"])
    history = spark.createDataFrame([], ["actor_id", "actor_name", "start_date", "end_date"])
    actors_path = str(tmp_path / "actors")
    history_path = str(tmp_path / "history")
    output_path = str(tmp_path / "backfill")
    actors.write.parquet(actors_path)
    history.write.parquet(history_path)

    backfill_actors_history_scd(actors_path, history_path, output_path)
    result = spark.read.parquet(output_path).collect()
    assert result[0]["actor_id"] == "a1"