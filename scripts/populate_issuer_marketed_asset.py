import psycopg2
import os
from biograph.core.normalize import normalize_company_name
from biograph.core.match import match_holder_to_issuer

DB_CONN_STR = os.environ.get("BIOGRAPH_DB_URL", "dbname=biograph user=biograph password=biograph host=localhost")

OB_QUERY = '''
    SELECT id, appl_no, product_no, approval_date, type, applicant_full_name, ingredient, trade_name
    FROM orange_book_product
'''
PB_QUERY = '''
    SELECT id, bla_number, applicant_full_name, proper_name, proprietary_name, approval_date
    FROM purple_book_product
'''

INSERT_SQL = '''
    INSERT INTO issuer_marketed_asset (
        issuer_id, asset_type, asset_id, regulatory_source, application_id,
        product_name, ingredient_or_proper_name, marketing_status, approval_date,
        holder_name_raw, match_confidence
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (issuer_id, asset_id, regulatory_source, application_id) DO UPDATE
    SET product_name = EXCLUDED.product_name,
        ingredient_or_proper_name = EXCLUDED.ingredient_or_proper_name,
        marketing_status = EXCLUDED.marketing_status,
        approval_date = EXCLUDED.approval_date,
        holder_name_raw = EXCLUDED.holder_name_raw,
        match_confidence = EXCLUDED.match_confidence
'''

def process_orange_book(conn):
    with conn.cursor() as cur:
        cur.execute(OB_QUERY)
        for row in cur.fetchall():
            ob_id, appl_no, product_no, approval_date, ob_type, applicant, ingredient, trade_name = row
            issuer_id, match_method, match_conf = match_holder_to_issuer(applicant, conn)
            if issuer_id:
                cur.execute(INSERT_SQL, (
                    issuer_id, 'SMALL_MOLECULE', ingredient, 'ORANGE_BOOK', appl_no,
                    trade_name, ingredient, ob_type, approval_date, applicant, match_conf
                ))
    conn.commit()

def process_purple_book(conn):
    with conn.cursor() as cur:
        cur.execute(PB_QUERY)
        for row in cur.fetchall():
            pb_id, bla_number, applicant, proper_name, proprietary_name, approval_date = row
            issuer_id, match_method, match_conf = match_holder_to_issuer(applicant, conn)
            if issuer_id:
                cur.execute(INSERT_SQL, (
                    issuer_id, 'BIOLOGIC', bla_number, 'PURPLE_BOOK', bla_number,
                    proprietary_name, proper_name, None, approval_date, applicant, match_conf
                ))
    conn.commit()

def main():
    conn = psycopg2.connect(DB_CONN_STR)
    process_orange_book(conn)
    process_purple_book(conn)
    print("issuer_marketed_asset population complete.")

if __name__ == "__main__":
    main()
