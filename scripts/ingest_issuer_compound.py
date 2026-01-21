import csv
import psycopg2
import sys
import os
from datetime import datetime, timezone

DB_CONN = os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"
CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "ingestion_data/issuer_compound.csv"

def main():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    with open(CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cur.execute("""
                INSERT INTO issuer_compound (issuer_id, compound_id, status, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (issuer_id, compound_id) DO UPDATE SET
                  status=EXCLUDED.status
            """, (
                row['issuer_id'],
                row['compound_id'],
                row.get('status'),
                datetime.now(timezone.utc)
            ))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
