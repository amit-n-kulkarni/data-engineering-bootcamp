from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, sum, broadcast

# Initialize Spark
spark = SparkSession.builder \
    .appName("HaloDataAnalysis") \
    .getOrCreate()

# Disable automatic broadcast join
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

# Load datasets (replace paths with actual sources)
match_details = spark.read.parquet("/path/match_details")
matches = spark.read.parquet("/path/matches")
medals_matches_players = spark.read.parquet("/path/medals_matches_players")
medals = spark.read.parquet("/path/medals")
maps = spark.read.parquet("/path/maps")

# ==============================================
# 1. Bucketed Tables on match_id
# ==============================================
match_details.write.bucketBy(16, "match_id").sortBy("match_id").saveAsTable("bucketed_match_details")
matches.write.bucketBy(16, "match_id").sortBy("match_id").saveAsTable("bucketed_matches")
medals_matches_players.write.bucketBy(16, "match_id").sortBy("match_id").saveAsTable("bucketed_medals_matches_players")

bucketed_match_details = spark.table("bucketed_match_details")
bucketed_matches = spark.table("bucketed_matches")
bucketed_medals_matches_players = spark.table("bucketed_medals_matches_players")

# ==============================================
# 2. Join DataFrames
# ==============================================
# Broadcast join for medals and maps
joined_df = bucketed_match_details \
    .join(bucketed_matches, "match_id") \
    .join(bucketed_medals_matches_players, "match_id") \
    .join(broadcast(medals), "medal_id") \
    .join(broadcast(maps), "map_id")

# ==============================================
# 3. Aggregations
# ==============================================

# Q1: Which player averages the most kills per game?
kills_per_player = joined_df.groupBy("player_id") \
    .agg(avg("kills").alias("avg_kills")) \
    .orderBy(col("avg_kills").desc())

# Q2: Which playlist gets played the most?
playlist_count = joined_df.groupBy("playlist_id") \
    .agg(count("match_id").alias("games_played")) \
    .orderBy(col("games_played").desc())

# Q3: Which map gets played the most?
map_count = joined_df.groupBy("map_id") \
    .agg(count("match_id").alias("games_played")) \
    .orderBy(col("games_played").desc())

# Q4: Which map do players get the most Killing Spree medals on?
killing_spree_medals = joined_df.filter(col("medal_name") == "Killing Spree") \
    .groupBy("map_id") \
    .agg(count("medal_id").alias("killing_spree_count")) \
    .orderBy(col("killing_spree_count").desc())

# ==============================================
# 4. Experiment with sortWithinPartitions
# ==============================================

# Try sorting by low-cardinality columns: playlist_id and map_id
sorted_by_playlist = joined_df.sortWithinPartitions("playlist_id")
sorted_by_map = joined_df.sortWithinPartitions("map_id")

# ==============================================
# 5. Save Results
# ==============================================
kills_per_player.write.mode("overwrite").parquet("/output/kills_per_player")
playlist_count.write.mode("overwrite").parquet("/output/playlist_count")
map_count.write.mode("overwrite").parquet("/output/map_count")
killing_spree_medals.write.mode("overwrite").parquet("/output/killing_spree_medals")

spark.stop()
