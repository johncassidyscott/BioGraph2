import psycopg2
from biograph.core.evidence import create_evidence
import requests

import psycopg2
from biograph.core.evidence import create_evidence
import requests
from datetime import datetime
import logging

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

logging.basicConfig(filename='edgar_ingest.log', level=logging.INFO, format='%(asctime)s %(message)s')

print("Starting EDGAR exhibits ingestion...")

def ingest_edgar_exhibits():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT id, accession, issuer_id FROM filing;")
    filings = cur.fetchall()
    print(f"Found {len(filings)} filings to process.")
    logging.info(f"Found {len(filings)} filings to process.")
    for filing_id, accession, issuer_id in filings:
        acc_no = accession.replace('-', '')
        cik = issuer_id.replace('ISS_', '')
        index_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no}/index.json"
        headers = {"User-Agent": "BioGraph2/1.0 (john.cassidy.scott@gmail.com)"}
        print(f"Fetching exhibit index for accession {accession} (CIK: {cik}) at {index_url}")
        resp = requests.get(index_url, headers=headers)
        print(f"Response status for {accession}: {resp.status_code}")
        logging.info(f"Exhibit index response for {accession}: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Failed to fetch exhibit index for accession {accession}")
            logging.warning(f"Failed to fetch exhibit index for accession {accession}")
            continue
        try:
            data = resp.json()
        except Exception as e:
            print(f"JSON decode error for accession {accession}: {e}")
            logging.error(f"JSON decode error for accession {accession}: {e}")
            continue
        items = data.get('directory', {}).get('item', [])
        print(f"Found {len(items)} items in exhibit index for accession {accession}")
        for doc in items:
            # Only process exhibits (typically .htm, .pdf, .txt, etc. and not the main filing)
            if doc.get('name', '').startswith('ex') or 'exhibit' in doc.get('name', '').lower():
                print(f"Inserting exhibit: {doc.get('name')} for filing {filing_id}")
                cur.execute("""
                    INSERT INTO exhibit (filing_id, exhibit_type, description, url, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    filing_id,
                    doc.get('name'),
                    doc.get('description', doc.get('name')),
                    f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no}/{doc.get('name')}",
                    datetime.utcnow()
                ))
                create_evidence('edgar_exhibit', accession, datetime.utcnow().date(), 'public', doc_uri=f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no}/{doc.get('name')}")
    conn.commit()
    cur.close()
    conn.close()
