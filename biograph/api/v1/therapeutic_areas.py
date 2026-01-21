from fastapi import APIRouter
import psycopg2
import os

router = APIRouter()

DB_CONN = os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

@router.get("/therapeutic-areas")
def get_therapeutic_areas():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT ta_id, ta_name, description FROM therapeutic_area;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"ta_id": r[0], "ta_name": r[1], "description": r[2]} for r in rows
    ]

@router.get("/therapeutic-areas/{ta_id}")
def get_therapeutic_area(ta_id: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT ta_id, ta_name, description FROM therapeutic_area WHERE ta_id = %s;", (ta_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"ta_id": row[0], "ta_name": row[1], "description": row[2]}
    return {}

@router.get("/therapeutic-areas/{ta_id}/compounds")
def get_ta_compounds(ta_id: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT c.compound_id, c.preferred_name, c.molecule_type
        FROM compound_therapeutic_area cta
        JOIN compound c ON cta.compound_id = c.compound_id
        WHERE cta.ta_id = %s;
    """, (ta_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"compound_id": r[0], "preferred_name": r[1], "molecule_type": r[2]} for r in rows
    ]

@router.get("/therapeutic-areas/{ta_id}/issuers")
def get_ta_issuers(ta_id: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT i.issuer_id, i.issuer_name, i.ticker
        FROM compound_therapeutic_area cta
        JOIN issuer_compound ic ON cta.compound_id = ic.compound_id
        JOIN issuer i ON ic.issuer_id = i.issuer_id
        WHERE cta.ta_id = %s;
    """, (ta_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"issuer_id": r[0], "issuer_name": r[1], "ticker": r[2]} for r in rows
    ]
