import pytest
from pyspark.sql import SparkSession
from ..jobs.top_playlist import most_played_playlist

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[2]").appName("TestTopPlaylist").getOrCreate()

def test_top_playlist(spark, tmp_path):
    # Fake input data
    input_data = [
        ("pl1",), ("pl2",), ("pl1",), ("pl3",), ("pl1",)
    ]
    df = spark.createDataFrame(input_data, ["playlist_id"])
    input_path = str(tmp_path / "input")
    output_path = str(tmp_path / "output")
    df.write.parquet(input_path)

    # Run job
    most_played_playlist(input_path, output_path)

    # Read output
    result = spark.read.parquet(output_path).collect()[0]
    
    assert result['playlist_id'] == "pl1"
    assert result['games_played'] == 3
