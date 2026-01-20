import psycopg2
from biograph.core.evidence import create_evidence
from biograph.core.assertions import create_assertion_with_evidence
import csv
from datetime import datetime

DB_CONN = "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"

CSV_PATH = "ingestion_data/program_registry.csv"

CURATION_SOURCE = "curation"
LICENSE = "internal"


def ingest_program_registry():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    with open(CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            issuer_id = row['issuer_id']
            program_name = row['program_name']
            cur.execute("""
                INSERT INTO program (issuer_id, program_name, created_at)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id;
            """, (issuer_id, program_name, datetime.utcnow()))
            program_id = cur.fetchone()[0] if cur.rowcount else None
            if 'alias' in row and row['alias']:
                cur.execute("""
                    INSERT INTO program_alias (program_id, alias)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                """, (program_id, row['alias']))
            evidence_id = create_evidence(CURATION_SOURCE, program_name, datetime.utcnow().date(), LICENSE)
            create_assertion_with_evidence('issuer_has_program', 'issuer', issuer_id, 'program', str(program_id), 1.0, datetime.utcnow().date(), [evidence_id])
    conn.commit()
    cur.close()
    conn.close()
