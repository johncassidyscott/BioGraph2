
import psycopg2
from biograph.core.assertions import create_assertion_with_evidence
from biograph.core.evidence import create_evidence
import csv
import sys
import os
from datetime import datetime

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"
CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "ingestion_data/program_registry.csv"
CURATION_SOURCE = "curation"
LICENSE = "internal"

def slugify(text):
    return text.lower().replace(' ', '-').replace('/', '-').replace('_', '-')

def get_issuer_id_map(cur):
    cur.execute("SELECT issuer_id, primary_cik FROM issuer")
    return {row[1].lstrip('CIK_').lstrip('0'): row[0] for row in cur.fetchall()}

def upsert_program(cur, issuer_id, name, slug, chembl_id):
    cur.execute("""
        INSERT INTO program (issuer_id, program_name, slug, chembl_id, created_at, updated_at)
        VALUES (%s, %s, %s, %s, now(), now())
        ON CONFLICT (issuer_id, slug) DO UPDATE SET
            program_name=EXCLUDED.program_name,
            chembl_id=EXCLUDED.chembl_id,
            updated_at=now()
        RETURNING id;
    """, (issuer_id, name, slug, chembl_id))
    return cur.fetchone()[0]

def upsert_program_alias(cur, program_id, alias_text, source):
    cur.execute("""
        INSERT INTO program_alias (program_id, alias)
        VALUES (%s, %s)
        ON CONFLICT (program_id, alias) DO NOTHING;
    """, (program_id, alias_text))

def main():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    issuer_map = get_issuer_id_map(cur)
    csv_version = os.path.basename(CSV_PATH)
    with open(CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            cik = row['issuer_cik'].lstrip('CIK_').lstrip('0')
            name = row['program_name'].strip()
            chembl_id = row.get('chembl_id', '').strip() or None
            notes = row.get('notes', '').strip() or None
            slug = slugify(name)
            if cik not in issuer_map:
                print(f"Skipping unknown issuer_cik: {cik}")
                continue
            issuer_id = issuer_map[cik]
            program_id = upsert_program(cur, issuer_id, name, slug, chembl_id)
            if notes:
                upsert_program_alias(cur, program_id, notes, CURATION_SOURCE)
            # Evidence and assertion
            evidence_id = create_evidence(
                CURATION_SOURCE,
                f"{csv_version}:{i+1}",
                datetime.utcnow().isoformat(),
                LICENSE
            )
            create_assertion_with_evidence(
                'issuer_has_program',
                'issuer',
                issuer_id,
                'program',
                program_id,
                1.0,
                datetime.utcnow().isoformat(),
                [evidence_id]
            )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
