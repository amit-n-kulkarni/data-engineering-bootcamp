from pyspark.sql import SparkSession

def highest_matches_paylist_transformation(spark, dataframe, ds):
    query = f"""
    SELECT playlist_id, COUNT(*) AS games_played
    FROM matches
    GROUP BY playlist_id
    ORDER BY games_played DESC
    """
    dataframe.createOrReplaceTempView("matches")
    return spark.sql(query)


def main():
    ds = '2025-01-01'
    spark = SparkSession.builder \
      .master("local") \
      .appName("spark_app_1") \
      .getOrCreate()
    output_df = highest_matches_paylist_transformation(spark, spark.table("highest_matches_paylist"), ds)
    output_df.write.mode("overwrite").insertInto("highest_matches_paylist")