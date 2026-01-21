# Marketed Assets Ingest & Rebuild Runbook

This runbook documents the deterministic, repeatable workflow for ingesting FDA Orange Book and Purple Book data, rebuilding the unified marketed assets table, and producing coverage and unmatched outputs.

## 1. Orange Book Ingest
- Ingest the latest (or specific month) Orange Book data:
  ```sh
  python scripts/ingest_orange_book.py --month <YYYY-MM>
  # or omit --month for latest
  ```
- Verify rowcount in `orange_book_product_raw`:
  ```sh
  ql -c "SELECT COUNT(*) FROM orange_book_product_raw;"
  ```

## 2. Purple Book Ingest
- Ingest the latest (or specific month) Purple Book data:
  ```sh
  python scripts/ingest_purple_book.py --month <YYYY-MM>
  # or omit --month for latest
  ```
- Verify rowcount in `purple_book_product_raw`:
  ```sh
  ql -c "SELECT COUNT(*) FROM purple_book_product_raw;"
  ```

## 3. Rebuild Unified Marketed Assets
- Rebuild the unified marketed assets table:
  ```sh
  python scripts/rebuild_issuer_marketed_assets.py
  ```
- Verify rowcount in `issuer_marketed_asset`:
  ```sh
  ql -c "SELECT COUNT(*) FROM issuer_marketed_asset;"
  ```

## 4. Required Output Files
After running the rebuild script, the following files will be written to `outputs/`:
- `outputs/unmatched_holders.csv`
- `outputs/heuristic_candidates.csv`
- `outputs/marketed_asset_qc.txt` (contains coverage metrics)

## 5. QC Metrics (printed and saved)
- Total # of issuers
- # of issuers with ≥1 marketed asset
- Coverage %
- Top 50 unmatched holders by frequency
- Top 50 issuers by asset count
- Flags:
  - Same `application_id` mapped to multiple issuers with HIGH confidence

## 6. Manual Alias Addition Loop
If coverage is low or unmatched holders remain, add an alias and rerun:
- Add an alias:
  ```sh
  python scripts/add_issuer_alias.py --issuer_id <id> --alias "<FDA holder>" --source fda_holder
  ```
- Rerun the rebuild:
  ```sh
  python scripts/rebuild_issuer_marketed_assets.py
  ```
- Recheck coverage and unmatched outputs.

---

**Note:** Do not change taxonomy tables at this stage. Only ingest FDA data, map to issuers, and produce coverage + unmatched outputs as described above.
