import pytest
import psycopg2
from scripts.ingest_edgar_exhibits import ingest_edgar_exhibits
from scripts.ingest_form4 import ingest_form4
from scripts.ingest_program_registry import ingest_program_registry

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

def test_ingest_edgar_exhibits_idempotent():
    ingest_edgar_exhibits()
    count1 = get_exhibit_count()
    ingest_edgar_exhibits()
    count2 = get_exhibit_count()
    assert count1 == count2

def test_ingest_form4_idempotent():
    ingest_form4()
    count1 = get_form4_count()
    ingest_form4()
    count2 = get_form4_count()
    assert count1 == count2

def test_ingest_program_registry_idempotent():
    ingest_program_registry()
    count1 = get_program_count()
    ingest_program_registry()
    count2 = get_program_count()
    assert count1 == count2

def get_exhibit_count():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM exhibit;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

def get_form4_count():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM insider_transaction;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

def get_program_count():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM program;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count
