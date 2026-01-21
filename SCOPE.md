# BioGraph Commercial POC Scope (Locked)

## Authoritative Model
- Only first-class entities: issuer, compound, therapeutic_area
- Only relationships: issuer_compound, compound_therapeutic_area
- Regulatory/ontology data (MeSH, ChEMBL, FDA) are reference only

## Data Model
- issuer(issuer_id, issuer_name, ticker, created_at)
- compound(compound_id, preferred_name, molecule_type, created_at)
- therapeutic_area(ta_id, ta_name, description, created_at)
- issuer_compound(issuer_id, compound_id, status, created_at)
- compound_therapeutic_area(compound_id, ta_id, created_at)

## Ingest Path
- issuer: CSV
- compound: CSV
- therapeutic_area: CSV (user-built from MeSH export)
- issuer_compound: CSV
- compound_therapeutic_area: CSV
- All ingest scripts are idempotent, explicit, non-inferential

## API Surface (Read-Only)
- GET /api/v1/therapeutic-areas
- GET /api/v1/therapeutic-areas/{ta_id}/compounds
- GET /api/v1/therapeutic-areas/{ta_id}/issuers
- GET /api/v1/issuers
- GET /api/v1/issuers/{issuer_id}/compounds
- GET /api/v1/issuers/{issuer_id}/therapeutic-areas
- GET /api/v1/compounds
- GET /api/v1/compounds/{compound_id}/issuers
- GET /api/v1/compounds/{compound_id}/therapeutic-areas

## Explicit Out-of-Scope
- No disease, target, assertion, evidence, or program tables in core joins
- No biology-driven traversal or inference
- No NER/ER, Neo4j, or graph algorithms
- No expansion of legacy tables

## Commercial/Regulatory Focus
- Therapeutic Areas are commercial/regulatory groupings
- Biology (MeSH, OpenTargets) is context only
- Compounds = unit of competition
- Issuers = economic actors
- No inference without explicit mapping

## Guardrails
- Tests ensure no endpoint traverses disease → compound
- No ontology table participates in joins unless explicitly requested
- TA drilldowns use only mapping tables
- Ingest scripts are idempotent

## Migration Notes
- Legacy tables (program, disease, target, assertion, evidence, etc.) are unused and out-of-scope
- No silent reinterpretation of old data
- All new data is explicit and mapped
