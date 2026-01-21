-- 002_fda_marketed_assets.sql
-- Add issuer_alias table
CREATE TABLE IF NOT EXISTS issuer_alias (
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    alias_text TEXT NOT NULL,
    alias_norm TEXT NOT NULL,
    source_system TEXT NOT NULL, -- manual|sec_legal|fda_holder|historical_mna
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT now(),
    PRIMARY KEY (issuer_id, alias_norm)
);
CREATE INDEX IF NOT EXISTS idx_issuer_alias_alias_norm ON issuer_alias(alias_norm);

-- Add regulatory_holder_map table
CREATE TABLE IF NOT EXISTS regulatory_holder_map (
    holder_name_raw TEXT NOT NULL,
    holder_name_norm TEXT NOT NULL,
    issuer_id TEXT NULL REFERENCES issuer(issuer_id),
    match_method TEXT NOT NULL, -- exact_norm|alias|manual|heuristic
    match_confidence TEXT NOT NULL, -- HIGH|MEDIUM|LOW
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT now(),
    PRIMARY KEY (holder_name_norm)
);

-- Add orange_book_product_raw table
CREATE TABLE IF NOT EXISTS orange_book_product_raw (
    appl_no TEXT,
    product_no TEXT,
    ingredient TEXT,
    trade_name TEXT,
    applicant TEXT,
    applicant_full_name TEXT NULL,
    dosage_form_route TEXT NULL,
    strength TEXT NULL,
    approval_date DATE NULL,
    marketing_type TEXT NULL,
    applicant_norm TEXT,
    source_month TEXT,
    ingested_at TIMESTAMP DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_obpr_appl_no ON orange_book_product_raw(appl_no);
CREATE INDEX IF NOT EXISTS idx_obpr_applicant_norm ON orange_book_product_raw(applicant_norm);

-- Add purple_book_product_raw table
CREATE TABLE IF NOT EXISTS purple_book_product_raw (
    bla_number TEXT,
    proprietary_name TEXT NULL,
    proper_name TEXT NULL,
    applicant TEXT,
    applicant_norm TEXT,
    product_type TEXT NULL,
    source_month TEXT,
    ingested_at TIMESTAMP DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_pbpr_bla_number ON purple_book_product_raw(bla_number);
CREATE INDEX IF NOT EXISTS idx_pbpr_applicant_norm ON purple_book_product_raw(applicant_norm);

-- Add issuer_marketed_asset table
CREATE TABLE IF NOT EXISTS issuer_marketed_asset (
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    asset_type TEXT NOT NULL, -- SMALL_MOLECULE|BIOLOGIC
    application_id TEXT NOT NULL, -- NDA/ANDA/BLA + number
    product_name TEXT NULL,
    active_name TEXT NULL,
    approval_date DATE NULL,
    marketing_status TEXT NULL,
    holder_name_raw TEXT NOT NULL,
    match_method TEXT NOT NULL,
    match_confidence TEXT NOT NULL,
    source_system TEXT NOT NULL, -- ORANGE_BOOK|PURPLE_BOOK
    source_month TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    PRIMARY KEY (source_system, application_id, issuer_id)
);

-- Add legal_name_norm to issuer if not present
ALTER TABLE issuer ADD COLUMN IF NOT EXISTS legal_name_norm TEXT;
CREATE INDEX IF NOT EXISTS idx_issuer_legal_name_norm ON issuer(legal_name_norm);