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
