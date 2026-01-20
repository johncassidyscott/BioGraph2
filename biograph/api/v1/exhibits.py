from fastapi import APIRouter
import psycopg2

router = APIRouter()

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

@router.get("/issuers/{cik}/exhibits")
def get_exhibits(cik: str, form_type: str = None):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    query = "SELECT e.exhibit_id, e.filing_id, e.exhibit_type, e.description, e.url, e.created_at FROM exhibit e JOIN filing f ON e.filing_id = f.id WHERE f.issuer_id = %s"
    params = [cik]
    if form_type:
        query += " AND f.form_type = %s"
        params.append(form_type)
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "exhibit_id": r[0],
            "filing_id": r[1],
            "exhibit_type": r[2],
            "description": r[3],
            "url": r[4],
            "created_at": r[5]
        } for r in rows
    ]
