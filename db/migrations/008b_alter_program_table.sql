-- 008b_alter_program_table.sql
-- Add missing columns to existing program table if not present
ALTER TABLE program
    ADD COLUMN IF NOT EXISTS name TEXT,
    ADD COLUMN IF NOT EXISTS slug TEXT,
    ADD COLUMN IF NOT EXISTS chembl_id TEXT,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

-- Add unique constraint if not present
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'program_issuer_id_slug_key'
    ) THEN
        ALTER TABLE program ADD CONSTRAINT program_issuer_id_slug_key UNIQUE (issuer_id, slug);
    END IF;
END$$;
