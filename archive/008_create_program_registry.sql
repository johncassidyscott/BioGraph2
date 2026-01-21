-- 008_create_program_registry.sql

-- Create program table
CREATE TABLE IF NOT EXISTS program (
    program_id SERIAL PRIMARY KEY,
    issuer_id INTEGER NOT NULL REFERENCES issuer(issuer_id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    chembl_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE (issuer_id, slug)
);

-- Create program_alias table (optional)
CREATE TABLE IF NOT EXISTS program_alias (
    program_id INTEGER NOT NULL REFERENCES program(program_id),
    alias_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    source TEXT,
    PRIMARY KEY (program_id, alias_text)
);