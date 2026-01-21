import sys
import psycopg2
import os

# Usage: python promote_holder_match.py <holder_name_raw> <issuer_id>
# Adds a HIGH/manual mapping to regulatory_holder_map and issuer_alias

def main():
    if len(sys.argv) != 3:
        print("Usage: python promote_holder_match.py <holder_name_raw> <issuer_id>")
        sys.exit(1)
    holder_name_raw = sys.argv[1]
    issuer_id = sys.argv[2]
    DB_CONN = os.environ.get("BIOGRAPH_DB_URL", "dbname=biograph user=biograph password=biograph host=localhost")
    conn = psycopg2.connect(DB_CONN)
    with conn, conn.cursor() as cur:
        # Insert into regulatory_holder_map
        cur.execute("""
            INSERT INTO regulatory_holder_map (holder_name_raw, issuer_id, match_method, match_confidence)
            VALUES (%s, %s, 'manual', 'HIGH')
            ON CONFLICT (holder_name_raw) DO UPDATE SET issuer_id = EXCLUDED.issuer_id, match_method = 'manual', match_confidence = 'HIGH'
        """, (holder_name_raw, issuer_id))
        # Insert into issuer_alias
        cur.execute("""
            INSERT INTO issuer_alias (issuer_id, alias, alias_norm, source)
            VALUES (%s, %s, %s, 'fda_holder')
            ON CONFLICT DO NOTHING
        """, (issuer_id, holder_name_raw, holder_name_raw.lower()))
    print(f"Promoted: {holder_name_raw} -> {issuer_id}")

if __name__ == "__main__":
    main()
