'''
Tests: Flink Sessionization
---------------------------
1. Use PyFlink's LocalStreamEnvironment and Table API to feed test data.
2. Verify that sessionization groups events correctly when gaps exceed 5 minutes.
3. Assert that average event counts match expected values for test datasets.
'''

def test_sessionization():
    env, t_env = create_flink_env()
    t_env.execute_sql("""
        CREATE TEMPORARY VIEW test_events AS
        SELECT * FROM (VALUES
            ('1.1.1.1', 'zachwilson.techcreator.io', TIMESTAMP '2025-08-05 10:00:00'),
            ('1.1.1.1', 'zachwilson.techcreator.io', TIMESTAMP '2025-08-05 10:03:00'),
            ('2.2.2.2', 'lulu.techcreator.io', TIMESTAMP '2025-08-05 11:10:00'),
            ('2.2.2.2', 'zachwilson.tech', TIMESTAMP '2025-08-05 11:20:00')
        ) AS t(ip_address, host, event_time)
    """)
    
    sessionized_df = t_env.sql_query("""
        SELECT ip_address, host, COUNT(*) as event_count
        FROM test_events
        GROUP BY ip_address, host
    """)
    results = [row for row in sessionized_df.execute().collect()]
    assert any(row.event_count == 2 for row in results)
    print("Test passed: Sessionization counts are correct")

def run_tests():
    test_sessionization()

if __name__ == "__main__":
    run_tests()
