import psycopg2

conn = psycopg2.connect("postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM filing WHERE form_type = '4' AND filed_at >= '2025-01-01';")
count = cur.fetchone()[0]
print(f"Recent Form 4 filings since 2025-01-01: {count}")
cur.close()
conn.close()
