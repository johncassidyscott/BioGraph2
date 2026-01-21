import psycopg2
import os
from biograph.core.normalize import normalize_company_name

def match_holder_to_issuer(holder_name, conn):
    """
    Deterministic matching of FDA holder/applicant to issuer_id.
    Returns (issuer_id, match_method, match_confidence) or (None, 'unmatched', 'LOW')
    """
    holder_name_norm = normalize_company_name(holder_name)
    with conn.cursor() as cur:
        # 1. Exact match to issuer.legal_name_norm
        cur.execute("SELECT issuer_id FROM issuer WHERE legal_name_norm = %s;", (holder_name_norm,))
        row = cur.fetchone()
        if row:
            return row[0], 'legal_name', 'HIGH'
        # 2. Alias match
        cur.execute("SELECT issuer_id FROM issuer_alias WHERE alias_norm = %s;", (holder_name_norm,))
        row = cur.fetchone()
        if row:
            return row[0], 'alias', 'HIGH'
        # 3. Existing regulatory_holder_map (manual/approved)
        cur.execute("SELECT issuer_id, match_method, match_confidence FROM regulatory_holder_map WHERE holder_name_norm = %s AND issuer_id IS NOT NULL;", (holder_name_norm,))
        row = cur.fetchone()
        if row:
            return row[0], row[1], row[2]
        # 4. Heuristic token match (not auto-assigned)
        # (Example: contains all major tokens)
        # For now, just flag for review
        return None, 'heuristic', 'MEDIUM'
