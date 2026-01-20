-- Migration: Create evidence, assertion, and assertion_evidence tables

CREATE TABLE IF NOT EXISTS evidence (
    id SERIAL PRIMARY KEY,
    source_system TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    observed_at DATE NOT NULL,
    license TEXT NOT NULL,
    doc_uri TEXT,
    snippet TEXT,
    checksum TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assertion (
    id SERIAL PRIMARY KEY,
    assertion_type TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    confidence NUMERIC,
    observed_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assertion_evidence (
    assertion_id INTEGER NOT NULL REFERENCES assertion(id) ON DELETE CASCADE,
    evidence_id INTEGER NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    PRIMARY KEY (assertion_id, evidence_id)
);
