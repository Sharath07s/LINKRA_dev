import os
import psycopg2
conn = psycopg2.connect(
    host="aws-0-ap-northeast-1.pooler.supabase.com",
    database="postgres",
    user="postgres.zwsfjrcpwtbcimdjeefa",
    password="k2WTrE9xflMP3ols",
    port=5432
)
cur = conn.cursor()
cur.execute("SELECT badge_number, email FROM users LIMIT 10;")
users = cur.fetchall()
for u in users:
    print(u)
