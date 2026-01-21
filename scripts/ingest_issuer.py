import csv
import psycopg2
import sys
import os
from datetime import datetime, timezone

DB_CONN = os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"
CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "ingestion_data/issuer.csv"

def main():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    with open(CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            issuer_id = row.get('issuer_id')
            issuer_name = row.get('issuer_name') if 'issuer_name' in row else None
            ticker = row.get('ticker') if 'ticker' in row else None
            created_at = row.get('created_at') if 'created_at' in row else None
            if not issuer_id:
                continue  # skip rows without issuer_id
            cur.execute("""
                INSERT INTO issuer (issuer_id, issuer_name, ticker, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (issuer_id) DO UPDATE SET
                  issuer_name=EXCLUDED.issuer_name,
                  ticker=EXCLUDED.ticker
            """, (
                issuer_id,
                issuer_name,
                ticker,
                created_at or datetime.now(timezone.utc)
            ))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
