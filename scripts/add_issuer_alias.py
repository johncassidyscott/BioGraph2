import argparse
import os
import psycopg2
from biograph.core.normalize import normalize_company_name

DB_CONN_STR = os.environ.get("BIOGRAPH_DB_URL", "dbname=biograph user=biograph password=biograph host=localhost")

def add_issuer_alias(issuer_id, alias_text, source_system, notes=None):
    alias_norm = normalize_company_name(alias_text)
    with psycopg2.connect(DB_CONN_STR) as conn, conn.cursor() as cur:
        cur.execute('''
            INSERT INTO issuer_alias (issuer_id, alias_text, alias_norm, source_system, notes)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (issuer_id, alias_norm) DO NOTHING
        ''', (issuer_id, alias_text, alias_norm, source_system, notes))
        conn.commit()
    print(f"Alias added: {issuer_id} | {alias_text} ({alias_norm}) [{source_system}]")

def main():
    parser = argparse.ArgumentParser(description="Add an alias for an issuer.")
    parser.add_argument("--issuer_id", required=True)
    parser.add_argument("--alias", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--notes", default=None)
    args = parser.parse_args()
    add_issuer_alias(args.issuer_id, args.alias, args.source, args.notes)

if __name__ == "__main__":
    main()
