import psycopg2
from biograph.core.evidence import create_evidence
import requests

import requests
import xml.etree.ElementTree as ET
import logging
from datetime import datetime

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

logging.basicConfig(filename='edgar_ingest.log', level=logging.INFO, format='%(asctime)s %(message)s')

def ingest_form4():
    print("Starting Form 4 insider transaction ingestion...")
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT id, issuer_id, accession, url FROM filing WHERE form_type = '4' AND filed_at >= '2025-01-01';")
    filings = cur.fetchall()
    print(f"Found {len(filings)} Form 4 filings to process.")
        count = 0
        total = len(filings)
        for filing_id, issuer_id, accession, url in filings:
            print(f"Processing Form 4: {accession} for issuer {issuer_id}")
            xml_url = url if url.endswith('.xml') else url.replace('.htm', '.xml')
            if not xml_url.startswith('http://') and not xml_url.startswith('https://'):
                xml_url = f"https://www.sec.gov/Archives/{xml_url.lstrip('/')}"
            headers = {"User-Agent": "BioGraph2/1.0 (john.cassidy.scott@gmail.com)"}
            resp = requests.get(xml_url, headers=headers)
            logging.info(f"Fetching XML for {accession} from {xml_url}")
            if resp.status_code != 200:
                logging.warning(f"Failed to fetch XML for {accession} (status {resp.status_code})")
                continue
            try:
                root = ET.fromstring(resp.content)
            except Exception as e:
                logging.error(f"XML parse error for {accession}: {e}")
                continue
            txns = root.findall('.//nonDerivativeTransaction')
            if not txns:
                logging.info(f"No nonDerivativeTransaction found for {accession}")
            for txn in txns:
                name = root.findtext('.//reportingOwner//rptOwnerName')
                date = txn.findtext('.//transactionDate//value')
                txn_type = txn.findtext('.//transactionCoding//transactionCode')
                shares = txn.findtext('.//transactionAmounts//transactionShares//value')
                price = txn.findtext('.//transactionAmounts//transactionPricePerShare//value')
                try:
                    cur.execute("""
                        INSERT INTO insider_transaction (issuer_id, filing_accession, insider_name, transaction_date, transaction_type, shares, price)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (
                        issuer_id,
                        accession,
                        name,
                        date,
                        txn_type,
                        int(shares) if shares else None,
                        float(price) if price else None
                    ))
                    logging.info(f"Inserted transaction for {name} on {date}")
                except Exception as e:
                    logging.error(f"DB insert error for {accession}: {e}")
            count += 1
            if count % 100 == 0 or count == total:
                try:
                    conn.commit()
                    cur.close()
                    conn.close()
                    # Reconnect
                    conn = psycopg2.connect(DB_CONN)
                    cur = conn.cursor()
                    print(f"Committed and reconnected after {count} filings.")
                except Exception as e:
                    logging.error(f"Error during commit/reconnect: {e}")
        # Final commit and close
        conn.commit()
        cur.close()
        conn.close()

if __name__ == "__main__":
    ingest_form4()
