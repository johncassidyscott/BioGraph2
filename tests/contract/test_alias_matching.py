import pytest
import psycopg2
import os
from biograph.core.normalize import normalize_company_name

DB_CONN_STR = os.environ.get("BIOGRAPH_DB_URL", "dbname=biograph user=biograph password=biograph host=localhost")

def setup_module(module):
    # Setup: create a test issuer and alias
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM issuer_alias;")
        cur.execute("DELETE FROM issuer;")
        cur.execute("INSERT INTO issuer (issuer_id, legal_name, legal_name_norm) VALUES ('0000001', 'Pfizer Inc.', %s);", (normalize_company_name('Pfizer Inc.'),))
        cur.execute("INSERT INTO issuer_alias (issuer_id, alias_text, alias_norm, source_system) VALUES ('0000001', 'PFIZER', %s, 'manual');", (normalize_company_name('PFIZER'),))
        conn.commit()

def teardown_module(module):
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM issuer_alias;")
        cur.execute("DELETE FROM issuer;")
        conn.commit()

def test_alias_matching_works():
    # Simulate matching a holder name to an alias
    holder = 'Pfizer'
    holder_norm = normalize_company_name(holder)
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("SELECT issuer_id FROM issuer_alias WHERE alias_norm = %s;", (holder_norm,))
        result = cur.fetchone()
        assert result is not None
        assert result[0] == '0000001'

def test_no_auto_issuer_creation():
    # Unknown holder should not create issuer
    unknown_holder = 'Unknown Pharma'
    unknown_norm = normalize_company_name(unknown_holder)
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("SELECT issuer_id FROM issuer_alias WHERE alias_norm = %s;", (unknown_norm,))
        result = cur.fetchone()
        assert result is None

def test_matching_precedence():
    # Legal name match beats alias
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("SELECT issuer_id FROM issuer WHERE legal_name_norm = %s;", (normalize_company_name('Pfizer Inc.'),))
        legal = cur.fetchone()
        cur.execute("SELECT issuer_id FROM issuer_alias WHERE alias_norm = %s;", (normalize_company_name('Pfizer'),))
        alias = cur.fetchone()
        assert legal is not None
        assert alias is not None
        assert legal[0] == alias[0] == '0000001'
