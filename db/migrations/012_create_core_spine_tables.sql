-- Migration: Core tables for Issuer–Compound–Therapeutic Area POC

CREATE TABLE IF NOT EXISTS compound (
  compound_id TEXT PRIMARY KEY,
  preferred_name TEXT NOT NULL,
  molecule_type TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS therapeutic_area (
  ta_id TEXT PRIMARY KEY,
  ta_name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS issuer_compound (
  issuer_id TEXT NOT NULL REFERENCES issuer(issuer_id),
  compound_id TEXT NOT NULL REFERENCES compound(compound_id),
  status TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (issuer_id, compound_id)
);

CREATE TABLE IF NOT EXISTS compound_therapeutic_area (
  compound_id TEXT NOT NULL REFERENCES compound(compound_id),
  ta_id TEXT NOT NULL REFERENCES therapeutic_area(ta_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (compound_id, ta_id)
);
