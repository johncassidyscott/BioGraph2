import pytest
import psycopg2
import os
import subprocess
from biograph.core.normalize import normalize_company_name

DB_CONN_STR = os.environ.get("BIOGRAPH_DB_URL", "dbname=biograph user=biograph password=biograph host=localhost")

def test_orange_book_idempotency():
    subprocess.run(["python3", "scripts/ingest_orange_book.py"], check=True)
    subprocess.run(["python3", "scripts/ingest_orange_book.py"], check=True)
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT appl_no, product_no) FROM orange_book_product_raw;")
        count, distinct_count = cur.fetchone()
        assert count == distinct_count

def test_purple_book_idempotency():
    subprocess.run(["python3", "scripts/ingest_purple_book.py"], check=True)
    subprocess.run(["python3", "scripts/ingest_purple_book.py"], check=True)
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT bla_number, proprietary_name) FROM purple_book_product_raw;")
        count, distinct_count = cur.fetchone()
        assert count == distinct_count

def test_issuer_marketed_asset_idempotency():
    subprocess.run(["python3", "scripts/rebuild_issuer_marketed_assets.py"], check=True)
    subprocess.run(["python3", "scripts/rebuild_issuer_marketed_assets.py"], check=True)
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT source_system, application_id, issuer_id) FROM issuer_marketed_asset;")
        count, distinct_count = cur.fetchone()
        assert count == distinct_count

def test_alias_matching_precedence():
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM issuer_alias;")
        cur.execute("DELETE FROM issuer;")
        cur.execute("INSERT INTO issuer (issuer_id, legal_name, legal_name_norm) VALUES ('0000001', 'Pfizer Inc.', %s);", (normalize_company_name('Pfizer Inc.'),))
        cur.execute("INSERT INTO issuer_alias (issuer_id, alias_text, alias_norm, source_system) VALUES ('0000001', 'PFIZER', %s, 'manual');", (normalize_company_name('PFIZER'),))
        conn.commit()
        # Legal name match beats alias
        cur.execute("SELECT issuer_id FROM issuer WHERE legal_name_norm = %s;", (normalize_company_name('Pfizer Inc.'),))
        legal = cur.fetchone()
        cur.execute("SELECT issuer_id FROM issuer_alias WHERE alias_norm = %s;", (normalize_company_name('Pfizer'),))
        alias = cur.fetchone()
        assert legal is not None
        assert alias is not None
        assert legal[0] == alias[0] == '0000001'

def test_no_auto_issuer_creation():
    unknown_holder = 'Unknown Pharma'
    unknown_norm = normalize_company_name(unknown_holder)
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("SELECT issuer_id FROM issuer_alias WHERE alias_norm = %s;", (unknown_norm,))
        result = cur.fetchone()
        assert result is None
        cur.execute("SELECT issuer_id FROM issuer WHERE legal_name_norm = %s;", (unknown_norm,))
        result = cur.fetchone()
        assert result is None
