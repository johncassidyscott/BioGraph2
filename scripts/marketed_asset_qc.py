import psycopg2
import os
from collections import Counter

DB_CONN = os.environ.get("BIOGRAPH_DB_URL", "dbname=biograph user=biograph password=biograph host=localhost")

def main():
    conn = psycopg2.connect(DB_CONN)
    with conn, conn.cursor() as cur:
        # Issuers in universe
        cur.execute("SELECT COUNT(*) FROM issuer WHERE issuer_id IN (SELECT issuer_id FROM universe_membership)")
        n_universe = cur.fetchone()[0]
        # Issuers matched to ≥1 marketed asset
        cur.execute("SELECT COUNT(DISTINCT issuer_id) FROM v_issuer_market_assets")
        n_matched = cur.fetchone()[0]
        coverage = 100.0 * n_matched / n_universe if n_universe else 0
        print(f"# Issuers in universe: {n_universe}")
        print(f"# Issuers matched to ≥1 marketed asset: {n_matched}")
        print(f"Coverage: {coverage:.1f}%\n")
        # Top 50 unmatched holders by frequency
        cur.execute("SELECT holder_name_raw, COUNT(*) FROM issuer_marketed_asset WHERE issuer_id IS NULL GROUP BY holder_name_raw ORDER BY COUNT(*) DESC LIMIT 50")
        print("Top 50 unmatched holders:")
        for row in cur.fetchall():
            print(f"  {row[0]} ({row[1]})")
        print()
        # Top 50 issuers by marketed asset count
        cur.execute("SELECT issuer_id, COUNT(*) FROM issuer_marketed_asset WHERE issuer_id IS NOT NULL GROUP BY issuer_id ORDER BY COUNT(*) DESC LIMIT 50")
        print("Top 50 issuers by marketed asset count:")
        for row in cur.fetchall():
            print(f"  {row[0]} ({row[1]})")
        print()
        # Duplicate detection: same application_id mapped to multiple issuers with HIGH confidence
        cur.execute("""
            SELECT application_id, COUNT(DISTINCT issuer_id)
            FROM issuer_marketed_asset
            WHERE match_confidence = 'HIGH' AND issuer_id IS NOT NULL
            GROUP BY application_id
            HAVING COUNT(DISTINCT issuer_id) > 1
            LIMIT 50
        """)
        print("Potential duplicate application_id mappings (HIGH confidence):")
        for row in cur.fetchall():
            print(f"  {row[0]} mapped to {row[1]} issuers")
        print()
        # Duplicate detection: same holder_name_norm mapped to multiple issuers
        cur.execute("""
            SELECT holder_name_raw, COUNT(DISTINCT issuer_id)
            FROM issuer_marketed_asset
            WHERE issuer_id IS NOT NULL
            GROUP BY holder_name_raw
            HAVING COUNT(DISTINCT issuer_id) > 1
            LIMIT 50
        """)
        print("Potential duplicate holder_name_raw mappings:")
        for row in cur.fetchall():
            print(f"  {row[0]} mapped to {row[1]} issuers")

if __name__ == "__main__":
    main()
