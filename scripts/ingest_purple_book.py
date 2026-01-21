import csv
import requests
import os
from datetime import datetime
from biograph.core.normalize import normalize_company_name

PB_URL = os.environ.get("PURPLE_BOOK_URL", "https://purplebooksearch.fda.gov/downloads/monthlyextract.csv")

DB_CONN_STR = os.environ.get(
    "BIOGRAPH_DB_URL",
    "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"
)

import psycopg2

def download_purple_book_csv(csv_url, save_to):
    r = requests.get(csv_url)
    r.raise_for_status()
    with open(save_to, 'wb') as f:
        f.write(r.content)
    return save_to

def ingest_purple_book_products(db_conn, csv_path):
    with open(csv_path, encoding='utf-8') as f, db_conn.cursor() as cur:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            bla_number = row.get('BLA Number')
            proprietary_name = row.get('Proprietary Name')
            proper_name = row.get('Proper Name')
            applicant = row.get('Applicant (Holder)')
            applicant_norm = normalize_company_name(applicant) if applicant else None
            product_type = row.get('Product Type')
            source_month = datetime.now().strftime('%Y-%m')
            # Idempotent insert
            cur.execute('''
                INSERT INTO purple_book_product_raw (
                    bla_number, proprietary_name, proper_name, applicant, applicant_norm, product_type, source_month
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            ''', (
                bla_number, proprietary_name, proper_name, applicant, applicant_norm, product_type, source_month
            ))
            count += 1
        db_conn.commit()
        print(f"Inserted {count} Purple Book product rows.")

def main():
    save_to = "/tmp/purple_book.csv"
    csv_path = download_purple_book_csv(PB_URL, save_to)
    db_conn = psycopg2.connect(DB_CONN_STR)
    ingest_purple_book_products(db_conn, csv_path)
    print("Purple Book ingest complete.")

if __name__ == "__main__":
    main()
