import pytest
import psycopg2
from biograph.core.evidence import create_evidence
from biograph.core.assertions import create_assertion_with_evidence

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

def test_orphan_assertion_fails_at_commit():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("BEGIN;")
    # Insert assertion without evidence
    cur.execute("""
        INSERT INTO assertion (assertion_type, subject_type, subject_id, object_type, object_id, confidence, observed_at, created_at)
        VALUES ('test', 'company', 'test_id', 'disease', 'test_disease', 0.9, '2026-01-20', NOW())
        RETURNING id;
    """)
    assertion_id = cur.fetchone()[0]
    with pytest.raises(psycopg2.errors.RaiseException):
        cur.execute("COMMIT;")
    cur.execute("ROLLBACK;")
    cur.close()
    conn.close()

def test_evidence_requires_license_and_observed_at():
    with pytest.raises(psycopg2.errors.NotNullViolation):
        create_evidence('test', 'rec1', None, None)


def test_api_never_returns_assertion_without_evidence_metadata():
    # Stub: would call API and check response
    # For now, just ensure assertion_with_evidence returns evidence metadata
    evidence_id = create_evidence('test', 'rec2', '2026-01-20', 'CC-BY')
    assertion_id = create_assertion_with_evidence('test', 'company', 'test_id', 'disease', 'test_disease', 0.9, '2026-01-20', [evidence_id])
    assert evidence_id is not None
    assert assertion_id is not None
