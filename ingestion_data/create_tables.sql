-- Table: company
CREATE TABLE IF NOT EXISTS company (
    cik TEXT PRIMARY KEY,
    sec_legal_name TEXT NOT NULL,
    ticker TEXT NOT NULL,
    exchange TEXT NOT NULL
);

-- Table: issuer
CREATE TABLE IF NOT EXISTS issuer (
    issuer_id TEXT PRIMARY KEY,
    primary_cik TEXT NOT NULL REFERENCES company(cik)
);

-- Table: universe_membership
CREATE TABLE IF NOT EXISTS universe_membership (
    issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
    universe_id TEXT NOT NULL,
    start_date DATE NOT NULL
);
