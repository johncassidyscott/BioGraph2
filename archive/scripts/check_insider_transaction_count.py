import psycopg2
import os

conn = psycopg2.connect("postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM insider_transaction;")
count = cur.fetchone()[0]
print(f"insider_transaction row count: {count}")
cur.close()
conn.close()
