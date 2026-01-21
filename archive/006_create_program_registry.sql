-- Migration: Create program and program_alias tables

CREATE TABLE IF NOT EXISTS program (
    id SERIAL PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    program_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS program_alias (
    id SERIAL PRIMARY KEY,
    program_id INTEGER NOT NULL REFERENCES program(id) ON DELETE CASCADE,
    alias TEXT NOT NULL
);
