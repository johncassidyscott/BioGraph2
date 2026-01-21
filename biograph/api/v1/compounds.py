from fastapi import APIRouter
import psycopg2
import os

router = APIRouter()

DB_CONN = os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

@router.get("/compounds")
def get_compounds():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT compound_id, preferred_name, molecule_type FROM compound;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"compound_id": r[0], "preferred_name": r[1], "molecule_type": r[2]} for r in rows
    ]

@router.get("/compounds/{compound_id}")
def get_compound(compound_id: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT compound_id, preferred_name, molecule_type FROM compound WHERE compound_id = %s;", (compound_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"compound_id": row[0], "preferred_name": row[1], "molecule_type": row[2]}
    return {}

@router.get("/compounds/{compound_id}/issuers")
def get_compound_issuers(compound_id: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT i.issuer_id, i.issuer_name, i.ticker
        FROM issuer_compound ic
        JOIN issuer i ON ic.issuer_id = i.issuer_id
        WHERE ic.compound_id = %s;
    """, (compound_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"issuer_id": r[0], "issuer_name": r[1], "ticker": r[2]} for r in rows
    ]

@router.get("/compounds/{compound_id}/therapeutic-areas")
def get_compound_tas(compound_id: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT ta.ta_id, ta.ta_name, ta.description
        FROM compound_therapeutic_area cta
        JOIN therapeutic_area ta ON cta.ta_id = ta.ta_id
        WHERE cta.compound_id = %s;
    """, (compound_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"ta_id": r[0], "ta_name": r[1], "description": r[2]} for r in rows
    ]
