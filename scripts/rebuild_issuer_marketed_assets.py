import os
import csv
import psycopg2
from datetime import datetime
from biograph.core.normalize import normalize_company_name
from biograph.core.match import match_holder_to_issuer

DB_CONN_STR = os.environ.get("BIOGRAPH_DB_URL", "dbname=biograph user=biograph password=biograph host=localhost")

# Output files for review
UNMATCHED_HOLDERS_CSV = os.path.join("outputs", "unmatched_holders.csv")
HEURISTIC_CANDIDATES_CSV = os.path.join("outputs", "heuristic_candidates.csv")

def fetch_orange_book_products(cur):
    cur.execute("SELECT appl_no, product_no, ingredient, trade_name, applicant, applicant_norm, approval_date, marketing_type, source_month FROM orange_book_product_raw")
    for row in cur.fetchall():
        yield {
            'source_system': 'ORANGE_BOOK',
            'appl_no': row[0],
            'product_no': row[1],
            'active_name': row[2],
            'product_name': row[3],
            'holder_name_raw': row[4],
            'holder_name_norm': row[5],
            'approval_date': row[6],
            'marketing_status': row[7],
            'source_month': row[8],
            'asset_type': 'SMALL_MOLECULE',
            'application_id': f"NDA/ANDA:{row[0]}"
        }

def fetch_purple_book_products(cur):
    cur.execute("SELECT bla_number, proprietary_name, proper_name, applicant, applicant_norm, product_type, source_month FROM purple_book_product_raw")
    for row in cur.fetchall():
        yield {
            'source_system': 'PURPLE_BOOK',
            'appl_no': row[0],
            'product_no': None,
            'active_name': row[2],
            'product_name': row[1],
            'holder_name_raw': row[3],
            'holder_name_norm': row[4],
            'approval_date': None,
            'marketing_status': None,
            'source_month': row[6],
            'asset_type': 'BIOLOGIC',
            'application_id': f"BLA:{row[0]}"
        }

def main():
    conn = psycopg2.connect(DB_CONN_STR)
    with conn, conn.cursor() as cur:
        # Clear and rebuild issuer_marketed_asset
        cur.execute("DELETE FROM issuer_marketed_asset")
        conn.commit()
        unmatched = []
        heuristic = []
        # Process Orange Book
        for prod in fetch_orange_book_products(cur):
            issuer_id, match_method, match_conf = match_holder_to_issuer(prod['holder_name_raw'], conn)
            if issuer_id:
                cur.execute('''
                    INSERT INTO issuer_marketed_asset (
                        issuer_id, asset_type, application_id, product_name, active_name, approval_date, marketing_status, holder_name_raw, match_method, match_confidence, source_system, source_month
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                ''', (
                    issuer_id, prod['asset_type'], prod['application_id'], prod['product_name'], prod['active_name'], prod['approval_date'], prod['marketing_status'], prod['holder_name_raw'], match_method, match_conf, prod['source_system'], prod['source_month']
                ))
            elif match_method == 'heuristic':
                heuristic.append(prod)
            else:
                unmatched.append(prod)
        # Process Purple Book
        for prod in fetch_purple_book_products(cur):
            issuer_id, match_method, match_conf = match_holder_to_issuer(prod['holder_name_raw'], conn)
            if issuer_id:
                cur.execute('''
                    INSERT INTO issuer_marketed_asset (
                        issuer_id, asset_type, application_id, product_name, active_name, approval_date, marketing_status, holder_name_raw, match_method, match_confidence, source_system, source_month
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                ''', (
                    issuer_id, prod['asset_type'], prod['application_id'], prod['product_name'], prod['active_name'], prod['approval_date'], prod['marketing_status'], prod['holder_name_raw'], match_method, match_conf, prod['source_system'], prod['source_month']
                ))
            elif match_method == 'heuristic':
                heuristic.append(prod)
            else:
                unmatched.append(prod)
        conn.commit()
    # Write review CSVs
    os.makedirs("outputs", exist_ok=True)
    if unmatched:
        with open(UNMATCHED_HOLDERS_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=unmatched[0].keys())
            writer.writeheader()
            writer.writerows(unmatched)
    if heuristic:
        with open(HEURISTIC_CANDIDATES_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=heuristic[0].keys())
            writer.writeheader()
            writer.writerows(heuristic)
    print(f"Rebuild complete. {len(unmatched)} unmatched, {len(heuristic)} heuristic candidates.")

if __name__ == "__main__":
    main()
