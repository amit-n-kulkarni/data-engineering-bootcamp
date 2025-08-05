import pytest
from pyspark.sql import SparkSession
from ..jobs.top_players_kills import top_players_by_kills

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[2]").appName("TestTopPlayersKills").getOrCreate()

def test_top_players_kills(spark, tmp_path):
    # Fake input data
    input_data = [
        ("p1", 10), ("p2", 5), ("p1", 15), ("p3", 8)
    ]
    df = spark.createDataFrame(input_data, ["player_id", "kills"])
    input_path = str(tmp_path / "input")
    output_path = str(tmp_path / "output")
    df.write.parquet(input_path)

    # Run job
    top_players_by_kills(input_path, output_path)

    # Read output
    result = spark.read.parquet(output_path).collect()
    result_dict = {row['player_id']: row['total_kills'] for row in result}

    assert result_dict["p1"] == 25
    assert "p2" in result_dict
    

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
