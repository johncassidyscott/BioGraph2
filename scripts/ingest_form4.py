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
    headers = {"User-Agent": "BioGraph2/1.0 (john.cassidy.scott@gmail.com)"}
    for filing_id, issuer_id, accession in filings:
        url = FORM4_API.format(accession=accession)
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            import psycopg2
            import requests
            import xml.etree.ElementTree as ET
            from datetime import datetime
            import logging

            DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

            logging.basicConfig(filename='edgar_ingest.log', level=logging.INFO, format='%(asctime)s %(message)s')

            print("Starting Form 4 insider transaction ingestion...")

            def ingest_form4():
                conn = psycopg2.connect(DB_CONN)
                cur = conn.cursor()
                cur.execute("SELECT id, issuer_id, accession, url FROM filing WHERE form_type = '4' AND filed_at >= '2025-01-01';")
                filings = cur.fetchall()
                print(f"Found {len(filings)} Form 4 filings to process.")
                for filing_id, issuer_id, accession, url in filings:
                    print(f"Processing Form 4: {accession} for issuer {issuer_id}")
                    # Try to fetch XML (primary document)
                    xml_url = url if url.endswith('.xml') else url.replace('.htm', '.xml')
                    headers = {"User-Agent": "BioGraph2/1.0 (john.cassidy.scott@gmail.com)"}
                    resp = requests.get(xml_url, headers=headers)
                    import logging
                    logging.basicConfig(filename='edgar_ingest.log', level=logging.INFO, format='%(asctime)s %(message)s')
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
                conn.commit()
                cur.close()
                conn.close()
