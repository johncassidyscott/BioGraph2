# Marketed Assets Ingestion and Mapping

## Overview
This document describes the ingestion and mapping of FDA Orange Book and Purple Book products to issuers in our database. It details the schema, matching logic, and key limitations regarding regulatory holder identity versus economic ownership.

## FDA Datasets as Regulatory Source
- **Orange Book** and **Purple Book** are authoritative for product approvals, not for issuer identity.
- FDA "holder/applicant" names are stored raw and mapped to internal issuers via deterministic, auditable processes.

## Database Tables
- **orange_book_product**: Raw rows from FDA Orange Book Products.txt
- **purple_book_product**: Raw rows from FDA Purple Book monthly extract
- **regulatory_holder_map**: Maps FDA holder names (raw/normalized) to issuer_id with match method, confidence, and notes
- **issuer_alias**: Stores alternate names for issuers (e.g., tickers, historical names, FDA holder names) for matching only
- **issuer_marketed_asset**: Unified, derived table of marketed assets by issuer, asset type, and regulatory source

## Name Normalization
- All matching uses `normalize_company_name(text)`:
  - Uppercase
  - Remove punctuation
  - Collapse whitespace
  - Remove corporate suffixes (INC, LLC, LTD, etc.)
  - Conservative removal of common pharma tokens (if improves matching)

## Matching Precedence
1. **Exact Match (HIGH)**: holder_name_norm == issuer.legal_name_norm
2. **Alias Match (HIGH)**: holder_name_norm == issuer_alias.alias_norm
3. **Regulatory Holder Map (HIGH)**: holder_name_norm == regulatory_holder_map.holder_name_norm (manual/approved)
4. **Heuristic Token Match (MEDIUM)**: Token-set similarity/contains-all-major-tokens (flag for review, not auto-assigned)
5. **Unmatched**: Persist for future manual aliasing

## Rules and Safeguards
- **issuer_id** (CIK) is authoritative. No ML or fuzzy org resolution beyond deterministic heuristics.
- **issuer_alias** is a display/matching helper, never an identity source.
- Never auto-create new issuers from FDA holder names.
- Never overwrite issuer legal name from FDA strings.
- All mappings are auditable with match_method and confidence.

## Limitations
- FDA “holder/applicant” is regulatory/legal, not guaranteed current economic owner after M&A.
- **issuer_alias** captures historical/acquired/brand-name variants for deterministic matching only.
- Mappings may not reflect current commercial rights or ownership post-M&A.

## Review and Manual Intervention
- Unmatched or heuristic matches are retained for review, not dropped.
- CLI helper provided for safe alias addition.

## Auditing
- All mappings and matches are logged with method, confidence, and notes for traceability.

---
For questions or to propose improvements, contact the data stewardship team.
