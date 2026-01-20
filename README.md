# BioGraph2

BIOGRAPH — CLEAN-SLATE REPOSITORY README
================================

This README defines a from-scratch, minimal, commercial-grade foundation for BioGraph.
It is intentionally opinionated, boring, and constrained.

If something is not explicitly allowed here, it is OUT OF SCOPE.

--------------------------------------------------
1. What BioGraph Is
--------------------------------------------------

BioGraph is an investor-grade life sciences intelligence system.

It answers one question well:

"Why is this company moving — and what evidence supports that explanation?"

BioGraph is NOT:
- a discovery platform
- a research knowledge graph
- a scientific reasoning engine
- a free graph traversal playground

BioGraph IS:
- evidence-first
- deterministic
- auditable
- scoped to issuer → asset → mechanism → disease
- built for analysts, strategy, and corporate development

--------------------------------------------------
2. Product Principles (Non-Negotiable)
--------------------------------------------------

1. Evidence First
   - No relationship exists without evidence.
   - Evidence must have:
     - source_system
     - source_record_id
     - observed_at
     - license
   - The database enforces this.

2. Humans Decide
   - ML only suggests.
   - No auto-creation of canonical entities.
   - No auto-merges.
   - All acceptance is explicit and logged.

3. Thin Durable Core
   - Store stable IDs only.
   - Resolve labels on demand.
   - Cache with TTL.
   - No bulk ontology ingestion.

4. Fixed Explanation Chains
   - No free graph traversal.
   - Only:
     Company → Program → Target → Disease

5. Postgres Is Source of Truth
   - Neo4j is optional, read-only projection.
   - Graph can always be rebuilt from Postgres.

--------------------------------------------------
3. Scope (MVP)
--------------------------------------------------

IN SCOPE:
- US public issuers (CIK-anchored)
- Universe CSV (manual)
- Filings metadata (EDGAR)
- Evidence storage
- Deterministic enrichment (GeoNames, Wikidata optional)
- Manual or CLI-based curation
- Explanation materialization

OUT OF SCOPE:
- Pathways
- Variants
- Omics
- Trial arms/endpoints
- Patent claims
- Predictive modeling
- Autonomous agents

--------------------------------------------------
4. Canonical Identity
--------------------------------------------------

Company:
- Canonical ID: SEC CIK
- No fuzzy org resolution

Drug / Program:
- Internal issuer-scoped ID
- External references optional (ChEMBL)

Target:
- Stable external ID (Open Targets / Ensembl)

Disease:
- MeSH / EFO ID
- Product taxonomy mapped manually

--------------------------------------------------
5. Data Model (Conceptual)
--------------------------------------------------

Core Entities:
- company
- program
- target
- disease
- evidence

Operational Entities:
- nlp_run
- mention
- candidate
- duplicate_suggestion

Assertions:
- company_has_program
- program_targets_target
- target_associated_with_disease

Every assertion requires ≥1 evidence record.

--------------------------------------------------
6. Repository Structure (NEW)
--------------------------------------------------

biograph/
  api/
    main.py              # single FastAPI entrypoint
    v1/
      issuers.py
      explanations.py
      health.py
  core/
    confidence.py
    evidence.py
    assertions.py
  storage/
    postgres.py
    neo4j_projection.py  # optional
  integrations/
    geonames.py
    wikidata.py          # optional, enrichment only
    chembl.py
  curation/
    cli.py               # human-in-loop interface
  nlp/
    candidate_extractor.py
  er/
    duplicate_suggester.py

db/
  migrations/

scripts/
  ingest_universe.py
  golden_ingest.py

docs/
  SPEC.txt
  ARCHITECTURE.md
  INGEST_RULES.md

tests/
  contract/
  integration/

--------------------------------------------------
7. Ingestion Order (Locked)
--------------------------------------------------

1. Universe CSV
2. Issuer CIK lock
3. Filings metadata + evidence
4. Program registry (manual or curated)
5. Assertions (with evidence)
6. Optional projection to Neo4j

--------------------------------------------------
8. API Rules
--------------------------------------------------

- One runtime only
- Versioned: /api/v1/*
- Read-only for analysts
- No raw graph exposure
- Admin actions via CLI only (MVP)

--------------------------------------------------
9. Verification Gates
--------------------------------------------------

Before ingesting real data:
- Fresh DB migrations pass
- Tests pass twice (determinism)
- Golden ingest is idempotent
- Evidence-first enforced at DB commit
- /healthz passes

--------------------------------------------------
10. What “Done” Means
--------------------------------------------------

BioGraph is "ready" when:
- It can explain a real company movement
- Every claim links to auditable evidence
- No speculative joins exist
- The system can be rebuilt from scratch deterministically

--------------------------------------------------
11. What Comes Later (Explicitly Deferred)
--------------------------------------------------

- Full NER pipelines
- Web UI
- Multi-tenancy
- Billing
- Advanced analytics
- GraphQL
- Real-time updates

--------------------------------------------------
12. Final Rule
--------------------------------------------------

If you are unsure whether to add something:

DO NOT ADD IT.

Keep the system boring.
Keep it explainable.
Keep it commercial.

End of README.
