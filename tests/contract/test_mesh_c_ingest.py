import psycopg2
import os

def test_mesh_c_ingest_sanity():
    conn = psycopg2.connect(os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM mesh_tree_c WHERE tree_number LIKE 'C%'")
    count = cur.fetchone()[0]
    assert count > 0, "No C tree rows ingested"
    cur.execute("SELECT tree_number, tree_level FROM mesh_tree_c WHERE tree_number LIKE 'C%' LIMIT 100")
    for tree_number, tree_level in cur.fetchall():
        assert tree_level == tree_number.count('.') + 1, f"tree_level mismatch for {tree_number}"
    conn.close()

def test_idempotent_reload():
    conn = psycopg2.connect(os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM mesh_tree_c")
    before = cur.fetchone()[0]
    os.system('PYTHONPATH=. python3 scripts/ingest_mesh_c_from_xml.py')
    cur.execute("SELECT COUNT(*) FROM mesh_tree_c")
    after = cur.fetchone()[0]
    assert before == after, f"Row count changed after reload: {before} -> {after}"
    conn.close()
