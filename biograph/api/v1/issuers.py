
from fastapi import APIRouter
import psycopg2
import os

router = APIRouter()

DB_CONN = os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

@router.get("/issuers")
def get_issuers():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT issuer_id, issuer_name, ticker FROM issuer;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"issuer_id": r[0], "issuer_name": r[1], "ticker": r[2]} for r in rows
    ]

@router.get("/issuers/{issuer_id}")
def get_issuer(issuer_id: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT issuer_id, issuer_name, ticker FROM issuer WHERE issuer_id = %s;", (issuer_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"issuer_id": row[0], "issuer_name": row[1], "ticker": row[2]}
    return {}

@router.get("/issuers/{issuer_id}/compounds")
def get_issuer_compounds(issuer_id: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT c.compound_id, c.preferred_name, c.molecule_type
        FROM issuer_compound ic
        JOIN compound c ON ic.compound_id = c.compound_id
        WHERE ic.issuer_id = %s;
    """, (issuer_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"compound_id": r[0], "preferred_name": r[1], "molecule_type": r[2]} for r in rows
    ]

@router.get("/issuers/{issuer_id}/therapeutic-areas")
def get_issuer_tas(issuer_id: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT ta.ta_id, ta.ta_name, ta.description
        FROM issuer_compound ic
        JOIN compound_therapeutic_area cta ON ic.compound_id = cta.compound_id
        JOIN therapeutic_area ta ON cta.ta_id = ta.ta_id
        WHERE ic.issuer_id = %s
        GROUP BY ta.ta_id, ta.ta_name, ta.description;
    """, (issuer_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"ta_id": r[0], "ta_name": r[1], "description": r[2]} for r in rows
    ]
