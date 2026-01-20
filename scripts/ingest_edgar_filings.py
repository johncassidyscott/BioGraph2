import psycopg2
import requests
import json
from biograph.core.evidence import create_evidence
import logging

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

# Dummy EDGAR API endpoint for demonstration
EDGAR_API = "https://data.sec.gov/submissions/CIK{cik}.json"

N = 20

logging.basicConfig(filename='edgar_ingest.log', level=logging.INFO, format='%(asctime)s %(message)s')

def ingest_edgar_filings():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT issuer_id, primary_cik FROM issuer;")
    issuers = [(row[0], row[1].replace('CIK_', '')) for row in cur.fetchall()]
    for issuer_id, cik in issuers:
        filings_url = EDGAR_API.format(cik=cik)
        logging.info(f"Querying CIK: {cik} at {filings_url}")
        resp = requests.get(filings_url)
        logging.info(f"Response status for {cik}: {resp.status_code}")
        if resp.status_code != 200:
            logging.info(f"Failed to fetch filings for CIK {cik}")
            continue
        data = resp.json()
        filings = data.get('filings', {}).get('recent', {})
        logging.info(f"Found {len(filings.get('accessionNumber', []))} filings for CIK {cik}")
        for i in range(min(N, len(filings.get('accessionNumber', [])))):
            accession = filings['accessionNumber'][i]
            form_type = filings['form'][i]
            filed_at = filings['filingDate'][i]
            period = filings['periodOfReport'][i]
            url = filings['primaryDocument'][i]
            meta = json.dumps({k: filings[k][i] for k in filings if isinstance(filings[k], list) and len(filings[k]) > i})
            logging.info(f"Inserting filing: {accession} for issuer {issuer_id}")
            cur.execute("""
                INSERT INTO filing (issuer_id, accession, form_type, filed_at, period, url, metadata_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (issuer_id, accession, form_type, filed_at, period, url, meta))
            filing_id = cur.fetchone()[0]
            evidence_id = create_evidence('edgar', accession, filed_at, 'public', doc_uri=url)
            # Optionally link evidence to assertion or filing
    conn.commit()
    cur.close()
    conn.close()
