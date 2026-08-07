import duckdb

con = duckdb.connect("database/cfb.duckdb")

print()

print(con.sql("""
SELECT
    season,
    COUNT(*) AS plays
FROM plays_clean
GROUP BY season
ORDER BY season
""").df())

print()

print(con.sql("""
SELECT *
FROM plays_clean
WHERE offense='Michigan'
AND season=2025
LIMIT 5
""").df())

con.close()