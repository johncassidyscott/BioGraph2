-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_issuer_marketed_asset_issuer_id ON issuer_marketed_asset(issuer_id);
CREATE INDEX IF NOT EXISTS idx_issuer_marketed_asset_application_id ON issuer_marketed_asset(application_id);
CREATE INDEX IF NOT EXISTS idx_issuer_marketed_asset_active_name ON issuer_marketed_asset(active_name);
CREATE INDEX IF NOT EXISTS idx_issuer_marketed_asset_product_name ON issuer_marketed_asset(product_name);
CREATE INDEX IF NOT EXISTS idx_orange_book_product_raw_applicant_norm ON orange_book_product_raw(applicant_norm);
CREATE INDEX IF NOT EXISTS idx_purple_book_product_raw_applicant_norm ON purple_book_product_raw(applicant_norm);
CREATE INDEX IF NOT EXISTS idx_issuer_alias_alias_norm ON issuer_alias(alias_norm);
