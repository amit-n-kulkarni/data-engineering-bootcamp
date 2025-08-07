'''
Assumptions & Environment Setup
------------------------------
1. Apache Flink version 1.15+ with PyFlink is used.
2. The input data is streamed from Kafka with fields: ip_address (STRING), host (STRING), event_time (TIMESTAMP), and event_type (STRING).
3. Event time is used for windowing with watermarks allowing out-of-order data up to 1 minute.
4. Output is written to a sink table for querying, but here we use DataFrames for analytics.
5. The job uses session windows with a 5-minute gap.
6. Tests use a local in-memory environment (MiniCluster) with sample data.
'''

from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.table.window import Session
from pyflink.table import expressions as expr
from datetime import datetime

def create_flink_env():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
    settings = EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)
    return env, t_env

def define_source_table(t_env):
    t_env.execute_sql("""
        CREATE TABLE web_events (
            ip_address STRING,
            host STRING,
            event_time TIMESTAMP(3),
            WATERMARK FOR event_time AS event_time - INTERVAL '1' MINUTE
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'web_events',
            'properties.bootstrap.servers' = 'localhost:9092',
            'format' = 'json'
        )
    """)

def sessionize_events(t_env):
    return t_env.sql_query("""
        SELECT
            ip_address,
            host,
            SESSION_START(event_time, INTERVAL '5' MINUTE) AS session_start,
            SESSION_END(event_time, INTERVAL '5' MINUTE) AS session_end,
            COUNT(*) AS event_count
        FROM web_events
        GROUP BY ip_address, host, SESSION(event_time, INTERVAL '5' MINUTE)
    """)

def calculate_metrics(sessionized_df):
    # Average number of web events per session for Tech Creator
    avg_events = sessionized_df.filter(sessionized_df.host.like('%techcreator%')) \
                                   .group_by(sessionized_df.host) \
                                   .select(sessionized_df.host, expr.avg(sessionized_df.event_count).alias('avg_events'))
    
    # Compare results between specified hosts
    hosts = ["zachwilson.techcreator.io", "zachwilson.tech", "lulu.techcreator.io"]
    host_comparison = sessionized_df.filter(sessionized_df.host.isin(hosts)) \
                                      .group_by(sessionized_df.host) \
                                      .select(sessionized_df.host, expr.avg(sessionized_df.event_count).alias('avg_events'))
    return avg_events, host_comparison

def main():
    env, t_env = create_flink_env()
    define_source_table(t_env)
    sessionized_df = sessionize_events(t_env)
    avg_events, host_comparison = calculate_metrics(sessionized_df)

    avg_events.execute().print()
    host_comparison.execute().print()

if __name__ == "__main__":
    main()
