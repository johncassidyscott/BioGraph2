-- Migration: Create insider_transaction table

CREATE TABLE IF NOT EXISTS insider_transaction (
    id SERIAL PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    filing_accession TEXT NOT NULL,
    insider_name TEXT,
    transaction_date DATE,
    transaction_type TEXT,
    shares INTEGER,
    price NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
