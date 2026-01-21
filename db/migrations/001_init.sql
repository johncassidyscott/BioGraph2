-- 001_init.sql: Minimal schema for BioGraph2 FDA Marketed Assets scope

-- Core tables
CREATE TABLE company (
    cik TEXT PRIMARY KEY,
    company_name TEXT NOT NULL
);

CREATE TABLE issuer (
    issuer_id TEXT PRIMARY KEY,
    issuer_name TEXT NOT NULL,
    ticker TEXT,
    created_at TIMESTAMP,
    legal_name_norm TEXT
);

CREATE TABLE universe_membership (
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    universe_name TEXT NOT NULL,
    PRIMARY KEY (issuer_id, universe_name)
);

-- SEC content
CREATE TABLE filing (
    id SERIAL PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    accession TEXT NOT NULL,
    form_type TEXT,
    filed_at TIMESTAMP,
    period TEXT,
    url TEXT,
    metadata_json JSONB
);

CREATE INDEX filing_issuer_id_idx ON filing(issuer_id);

CREATE TABLE exhibit (
    exhibit_id SERIAL PRIMARY KEY,
    filing_id INTEGER NOT NULL REFERENCES filing(id),
    exhibit_type TEXT,
    description TEXT,
    url TEXT,
    created_at TIMESTAMP
);

CREATE INDEX exhibit_filing_id_idx ON exhibit(filing_id);

-- MeSH reference
CREATE TABLE mesh_descriptor (
    mesh_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE mesh_tree_c (
    mesh_id TEXT NOT NULL REFERENCES mesh_descriptor(mesh_id),
    tree_number TEXT NOT NULL,
    parent_tree_number TEXT,
    PRIMARY KEY (mesh_id, tree_number)
);

CREATE INDEX mesh_tree_c_tree_number_idx ON mesh_tree_c(tree_number);
CREATE INDEX mesh_tree_c_parent_tree_number_idx ON mesh_tree_c(parent_tree_number);

-- FDA raw ingest
CREATE TABLE orange_book_product_raw (
    id SERIAL PRIMARY KEY,
    appl_no TEXT NOT NULL,
    applicant TEXT NOT NULL,
    applicant_norm TEXT,
    product_name TEXT,
    ingredient TEXT,
    approval_date DATE,
    marketing_status TEXT
);
CREATE INDEX ob_applicant_norm_idx ON orange_book_product_raw(applicant_norm);
CREATE INDEX ob_appl_no_idx ON orange_book_product_raw(appl_no);

CREATE TABLE purple_book_product_raw (
    id SERIAL PRIMARY KEY,
    bla_number TEXT NOT NULL,
    applicant TEXT NOT NULL,
    applicant_norm TEXT,
    proper_name TEXT,
    approval_date DATE,
    marketing_status TEXT
);
CREATE INDEX pb_applicant_norm_idx ON purple_book_product_raw(applicant_norm);
CREATE INDEX pb_bla_number_idx ON purple_book_product_raw(bla_number);

-- Name mapping + safeguards
CREATE TABLE issuer_alias (
    id SERIAL PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    alias TEXT NOT NULL,
    alias_norm TEXT NOT NULL
);
CREATE INDEX issuer_alias_alias_norm_idx ON issuer_alias(alias_norm);

CREATE TABLE regulatory_holder_map (
    id SERIAL PRIMARY KEY,
    holder_name TEXT NOT NULL,
    holder_name_norm TEXT NOT NULL,
    issuer_id TEXT REFERENCES issuer(issuer_id),
    approved BOOLEAN NOT NULL DEFAULT FALSE
);

-- Derived marketed assets
CREATE TABLE issuer_marketed_asset (
    id SERIAL PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    asset_type TEXT NOT NULL,
    application_id TEXT NOT NULL,
    product_name TEXT,
    ingredient_or_proper_name TEXT,
    approval_date DATE,
    marketing_status TEXT,
    holder_name_raw TEXT,
    match_confidence TEXT,
    source_system TEXT
);
CREATE INDEX ima_issuer_id_idx ON issuer_marketed_asset(issuer_id);
CREATE INDEX ima_asset_type_idx ON issuer_marketed_asset(asset_type);
