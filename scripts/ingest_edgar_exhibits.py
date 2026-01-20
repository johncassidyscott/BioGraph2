import psycopg2
from biograph.core.evidence import create_evidence
import requests
from datetime import datetime

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

# Dummy endpoint for demonstration
EXHIBIT_API = "https://data.sec.gov/filings/{accession}/exhibits.json"

def ingest_edgar_exhibits():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT id, accession FROM filing;")
    filings = cur.fetchall()
    for filing_id, accession in filings:
        url = EXHIBIT_API.format(accession=accession)
        resp = requests.get(url)
        if resp.status_code != 200:
            continue
        data = resp.json()
        for exhibit in data.get('exhibits', []):
            cur.execute("""
                INSERT INTO exhibit (filing_id, exhibit_type, description, url, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;

            import psycopg2
            from biograph.core.evidence import create_evidence
            import requests
            from datetime import datetime

            DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

            def ingest_edgar_exhibits():
                conn = psycopg2.connect(DB_CONN)
                cur = conn.cursor()
                cur.execute("SELECT id, accession, issuer_id FROM filing;")
                filings = cur.fetchall()
                for filing_id, accession, issuer_id in filings:
                    # Parse accession to SEC format
                    acc_no = accession.replace('-', '')
                    cik = issuer_id.replace('ISS_', '')
                    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no}/index.json"
                    resp = requests.get(index_url, headers={"User-Agent": "BioGraph/1.0 johncassidyscott@gmail.com"})
                    if resp.status_code != 200:
                        continue
                    data = resp.json()
                    for doc in data.get('directory', {}).get('item', []):
                        # Only process exhibits (typically .htm, .pdf, .txt, etc. and not the main filing)
                        if doc.get('name', '').startswith('ex') or 'exhibit' in doc.get('name', '').lower():
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
