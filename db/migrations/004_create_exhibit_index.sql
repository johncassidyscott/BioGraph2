-- Migration: Create exhibit index table

CREATE TABLE IF NOT EXISTS exhibit (
    exhibit_id SERIAL PRIMARY KEY,
    filing_id INTEGER NOT NULL REFERENCES filing(id) ON DELETE CASCADE,
    exhibit_type TEXT,
    description TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
