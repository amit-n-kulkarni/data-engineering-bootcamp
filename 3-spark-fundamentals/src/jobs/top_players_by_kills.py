from pyspark.sql import SparkSession

def top_players_by_kills_transformation(spark, dataframe, ds):
    query = f"""
    SELECT player_id, SUM(kills) AS total_kills
    FROM match_details
    GROUP BY player_id
    ORDER BY total_kills DESC
    """
    dataframe.createOrReplaceTempView("match_details")
    return spark.sql(query)


def main():
    ds = '2025-01-01'
    spark = SparkSession.builder \
      .master("local") \
      .appName("spark_app_1") \
      .getOrCreate()
    output_df = top_players_by_kills_transformation(spark, spark.table("top_players_by_kills"), ds)
    output_df.write.mode("overwrite").insertInto("top_players_by_kills")