from fastapi import APIRouter
import psycopg2
import os

router = APIRouter()

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

@router.get("/issuers")
def get_issuers():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT issuer_id, primary_cik FROM issuer;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"issuer_id": r[0], "primary_cik": r[1]} for r in rows]

@router.get("/issuers/{cik}")
def get_issuer(cik: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT issuer_id, primary_cik FROM issuer WHERE primary_cik = %s;", (cik,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"issuer_id": row[0], "primary_cik": row[1]}
    return {}

@router.get("/issuers/{cik}/filings")
def get_filings(cik: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT id, accession, form_type, filed_at, period, url FROM filing WHERE issuer_id = %s;", (cik,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "accession": r[1],
            "form_type": r[2],
            "filed_at": r[3],
            "period": r[4],
            "url": r[5]
        } for r in rows
    ]
