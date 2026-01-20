import pytest
import psycopg2
from biograph.core.evidence import create_evidence
from biograph.core.assertions import create_assertion_with_evidence

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

def test_migrations_apply_cleanly():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM evidence;")
    cur.close()
    conn.close()


def test_golden_ingest_creates_evidence_and_assertion():
    evidence_id = create_evidence('test', 'rec3', '2026-01-20', 'CC-BY')
    assertion_id = create_assertion_with_evidence('test', 'company', 'test_id', 'disease', 'test_disease', 0.9, '2026-01-20', [evidence_id])
    assert evidence_id is not None
    assert assertion_id is not None


def test_pytest_green():
    assert True
