import csv
import psycopg2
import sys
import os
from datetime import datetime, timezone

DB_CONN = os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"
CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "ingestion_data/compound.csv"

def main():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    with open(CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cur.execute("""
                INSERT INTO compound (compound_id, preferred_name, molecule_type, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (compound_id) DO UPDATE SET
                  preferred_name=EXCLUDED.preferred_name,
                  molecule_type=EXCLUDED.molecule_type
            """, (
                row['compound_id'],
                row['preferred_name'],
                row.get('molecule_type'),
                datetime.now(timezone.utc)
            ))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
