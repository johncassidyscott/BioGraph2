import psycopg2
from datetime import datetime

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

def create_evidence(source_system, source_record_id, observed_at, license, doc_uri=None, snippet=None, checksum=None):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO evidence (source_system, source_record_id, observed_at, license, doc_uri, snippet, checksum, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        source_system,
        source_record_id,
        observed_at,
        license,
        doc_uri,
        snippet,
        checksum,
        datetime.utcnow()
    ))
    evidence_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return evidence_id
