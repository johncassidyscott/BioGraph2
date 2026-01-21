-- 008c_alter_program_id.sql
-- Add program_id SERIAL PRIMARY KEY if not present
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_name='program' AND column_name='program_id'
    ) THEN
        ALTER TABLE program ADD COLUMN program_id SERIAL PRIMARY KEY;
    END IF;
END$$;

-- If there is an old id column, drop it (optional, only if not used elsewhere)
-- ALTER TABLE program DROP COLUMN IF EXISTS id;
