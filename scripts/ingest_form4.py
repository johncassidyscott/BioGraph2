import psycopg2
from biograph.core.evidence import create_evidence
import requests
from datetime import datetime

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

# Dummy endpoint for demonstration
FORM4_API = "https://data.sec.gov/filings/{accession}/form4.json"

def ingest_form4():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT id, issuer_id, accession FROM filing WHERE form_type = '4';")
    filings = cur.fetchall()
    for filing_id, issuer_id, accession in filings:
        url = FORM4_API.format(accession=accession)
        resp = requests.get(url)
        if resp.status_code != 200:
            continue
        data = resp.json()
        for tx in data.get('transactions', []):
            cur.execute("""
                INSERT INTO insider_transaction (issuer_id, filing_accession, insider_name, transaction_date, transaction_type, shares, price, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                issuer_id,
                accession,
                tx.get('insider_name'),
                tx.get('transaction_date'),
                tx.get('transaction_type'),
                tx.get('shares'),
                tx.get('price'),
                datetime.utcnow()
            ))
            create_evidence('form4', accession, tx.get('transaction_date'), 'public', doc_uri=url)
    conn.commit()
    cur.close()
    conn.close()
