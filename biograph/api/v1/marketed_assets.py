from fastapi import APIRouter
import psycopg2
import os
from typing import Optional

router = APIRouter()

DB_CONN = os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

@router.get("/marketed-assets/search")
def search_marketed_assets(q: str):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT issuer_id, asset_type, application_id, product_name, active_name, approval_date, marketing_status, source_system, source_month, match_method, match_confidence, holder_name_raw
        FROM v_issuer_market_assets
        WHERE product_name ILIKE %s OR active_name ILIKE %s
        LIMIT 100;
    """, (f"%{q}%", f"%{q}%"))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "issuer_id": r[0],
            "asset_type": r[1],
            "application_id": r[2],
            "product_name": r[3],
            "active_name": r[4],
            "approval_date": r[5],
            "marketing_status": r[6],
            "source_system": r[7],
            "source_month": r[8],
            "match_method": r[9],
            "match_confidence": r[10],
            "holder_name_raw": r[11],
        } for r in rows
    ]

@router.get("/issuers/{issuer_id}/marketed-assets")
def get_issuer_marketed_assets(issuer_id: str, status: Optional[str] = None):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    if status == "current":
        view = "v_issuer_market_assets_current"
    elif status == "ever":
        view = "v_issuer_market_assets_ever"
    else:
        view = "v_issuer_market_assets"
    cur.execute(f"""
        SELECT asset_type, application_id, product_name, active_name, approval_date, marketing_status, source_system, source_month, match_method, match_confidence, holder_name_raw
        FROM {view}
        WHERE issuer_id = %s
        ORDER BY approval_date DESC NULLS LAST;
    """, (issuer_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "asset_type": r[0],
            "application_id": r[1],
            "product_name": r[2],
            "active_name": r[3],
            "approval_date": r[4],
            "marketing_status": r[5],
            "source_system": r[6],
            "source_month": r[7],
            "match_method": r[8],
            "match_confidence": r[9],
            "holder_name_raw": r[10],
        } for r in rows
    ]

@router.get("/healthz")
def healthz():
    return {"status": "ok"}
