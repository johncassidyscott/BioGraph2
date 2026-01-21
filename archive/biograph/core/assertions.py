import psycopg2
from datetime import datetime

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

def create_assertion_with_evidence(assertion_type, subject_type, subject_id, object_type, object_id, confidence, observed_at, evidence_ids):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO assertion (assertion_type, subject_type, subject_id, object_type, object_id, confidence, observed_at, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        assertion_type,
        subject_type,
        subject_id,
        object_type,
        object_id,
        confidence,
        observed_at,
        datetime.utcnow()
    ))
    assertion_id = cur.fetchone()[0]
    for eid in evidence_ids:
        cur.execute("""
            INSERT INTO assertion_evidence (assertion_id, evidence_id)
            VALUES (%s, %s);
        """, (assertion_id, eid))
    conn.commit()
    cur.close()
    conn.close()
    return assertion_id
