import csv
import requests
import os
from datetime import datetime
from biograph.core.normalize import normalize_company_name

OB_URL = "https://www.accessdata.fda.gov/scripts/cder/ob/docs/obzip/Products.zip"
OB_PRODUCTS_FILENAME = "Products.txt"

DB_CONN_STR = os.environ.get(
    "BIOGRAPH_DB_URL",
    "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"
)

import psycopg2

def download_and_extract_products_txt(zip_url, extract_to):
    import zipfile
    import io
    r = requests.get(zip_url)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extract(OB_PRODUCTS_FILENAME, path=extract_to)
    return os.path.join(extract_to, OB_PRODUCTS_FILENAME)

def ingest_orange_book_products(db_conn, products_path):
    with open(products_path, encoding='utf-8') as f, db_conn.cursor() as cur:
        reader = csv.DictReader(f, delimiter='~')
        count = 0
        for row in reader:
            appl_no = row.get('Appl_No')
            product_no = row.get('Product_No')
            ingredient = row.get('Ingredient')
            trade_name = row.get('Trade_Name')
            applicant = row.get('Applicant') or row.get('Applicant_Full_Name')
            applicant_full_name = row.get('Applicant_Full_Name')
            dosage_form_route = row.get('Dosage_Form_Route')
            strength = row.get('Strength')
            approval_date_raw = row.get('Approval_Date')
            # Robust date parsing: set to None if not a valid YYYY-MM-DD
            approval_date = None
            if approval_date_raw:
                try:
                    approval_date = datetime.strptime(approval_date_raw, "%Y-%m-%d").date()
                except Exception:
                    approval_date = None
            marketing_type = row.get('Marketing_Status') or row.get('Type')
            source_month = datetime.now().strftime('%Y-%m')
            applicant_norm = normalize_company_name(applicant) if applicant else None
            # Idempotent insert
            cur.execute('''
                INSERT INTO orange_book_product_raw (
                    appl_no, product_no, ingredient, trade_name, applicant, applicant_full_name, dosage_form_route, strength, approval_date, marketing_type, applicant_norm, source_month
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            ''', (
                appl_no, product_no, ingredient, trade_name, applicant, applicant_full_name, dosage_form_route, strength, approval_date, marketing_type, applicant_norm, source_month
            ))
            count += 1
        db_conn.commit()
        print(f"Inserted {count} Orange Book product rows.")

def main():
    # Prefer local Products.txt or products.txt if available
    local_products_upper = os.path.join("ingestion_data", "Products.txt")
    local_products_lower = os.path.join("ingestion_data", "products.txt")
    if os.path.exists(local_products_upper):
        print(f"Using local Orange Book file: {local_products_upper}")
        products_path = local_products_upper
    elif os.path.exists(local_products_lower):
        print(f"Using local Orange Book file: {local_products_lower}")
        products_path = local_products_lower
    else:
        extract_to = "/tmp"
        print(f"Downloading Orange Book Products.zip from FDA website...")
        products_path = download_and_extract_products_txt(OB_URL, extract_to)
    db_conn = psycopg2.connect(DB_CONN_STR)
    ingest_orange_book_products(db_conn, products_path)
    print("Orange Book ingest complete.")

if __name__ == "__main__":
    main()
