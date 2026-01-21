-- Unified view for all marketed assets (OB + PB)
CREATE OR REPLACE VIEW v_issuer_market_assets AS
SELECT
  issuer_id,
  asset_type,
  application_id,
  product_name,
  active_name,
  approval_date,
  marketing_status,
  source_system,
  source_month,
  match_method,
  match_confidence,
  holder_name_raw
FROM issuer_marketed_asset;

-- Current marketed assets (exclude discontinued if possible)
CREATE OR REPLACE VIEW v_issuer_market_assets_current AS
SELECT * FROM v_issuer_market_assets
WHERE marketing_status NOT IN ('DISCN', 'Discontinued', 'WITHDRAWN', 'Withdrawn');

-- All ever-approved marketed assets
CREATE OR REPLACE VIEW v_issuer_market_assets_ever AS
SELECT * FROM v_issuer_market_assets
WHERE approval_date IS NOT NULL;