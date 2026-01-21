import pytest
import psycopg2
import os

DB_CONN_STR = os.environ.get("BIOGRAPH_DB_URL", "dbname=biograph user=biograph password=biograph host=localhost")

def test_ingest_idempotency():
    # Run ingest_orange_book.py and ingest_purple_book.py twice, check no duplicate rows
    import subprocess
    subprocess.run(["python3", "scripts/ingest_orange_book.py"], check=True)
    subprocess.run(["python3", "scripts/ingest_orange_book.py"], check=True)
    subprocess.run(["python3", "scripts/ingest_purple_book.py"], check=True)
    subprocess.run(["python3", "scripts/ingest_purple_book.py"], check=True)
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT id) FROM orange_book_product;")
        count, distinct_count = cur.fetchone()
        assert count == distinct_count
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT id) FROM purple_book_product;")
        count, distinct_count = cur.fetchone()
        assert count == distinct_count

def test_issuer_marketed_asset_idempotency():
    import subprocess
    subprocess.run(["python3", "scripts/populate_issuer_marketed_asset.py"], check=True)
    subprocess.run(["python3", "scripts/populate_issuer_marketed_asset.py"], check=True)
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT issuer_id, asset_id, regulatory_source, application_id) FROM issuer_marketed_asset;")
        count, distinct_count = cur.fetchone()
        assert count == distinct_count
