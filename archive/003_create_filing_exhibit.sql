-- Migration: Create filing and exhibit tables

CREATE TABLE IF NOT EXISTS filing (
    id SERIAL PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    accession TEXT NOT NULL,
    form_type TEXT NOT NULL,
    filed_at DATE NOT NULL,
    period TEXT,
    url TEXT,
    metadata_json JSONB
);

CREATE TABLE IF NOT EXISTS exhibit (
    id SERIAL PRIMARY KEY,
    filing_id INTEGER REFERENCES filing(id),
    metadata_json JSONB
);
