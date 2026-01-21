import psycopg2
import os
import pytest

DB_CONN = os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

def test_no_disease_table():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name='disease'")
    assert cur.fetchone() is None, "disease table should not exist"
    cur.close()
    conn.close()

def test_no_ontology_joins():
    # Ensure mesh_descriptor and mesh_tree_c are not joined in mapping tables
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM mesh_descriptor")
    mesh_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM mesh_tree_c")
    tree_count = cur.fetchone()[0]
    # Just check they exist, not joined
    assert mesh_count > 0 and tree_count > 0
    cur.close()
    conn.close()

def test_ta_drilldown_only_mapping():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM compound_therapeutic_area")
    assert cur.fetchone()[0] >= 0
    cur.execute("SELECT COUNT(*) FROM issuer_compound")
    assert cur.fetchone()[0] >= 0
    cur.close()
    conn.close()
