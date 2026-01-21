-- 010_alter_program_and_alias_issuer_id_to_text.sql

-- Change issuer_id in program table from INTEGER to TEXT
ALTER TABLE program ALTER COLUMN issuer_id TYPE TEXT;

-- Drop and recreate the foreign key constraint to issuer(issuer_id)
ALTER TABLE program DROP CONSTRAINT IF EXISTS program_issuer_id_fkey;
ALTER TABLE program ADD CONSTRAINT program_issuer_id_fkey FOREIGN KEY (issuer_id) REFERENCES issuer(issuer_id);

-- Change program_id in program_alias to TEXT if needed (if program_id is referenced as TEXT)
-- But program_id is SERIAL PRIMARY KEY (integer), so leave as is

-- No change needed for program_alias unless it references issuer_id directly (it does not)

-- If any other tables reference program.issuer_id as INTEGER, update them similarly.

-- Note: This migration assumes all existing issuer_id values in program are valid TEXT representations matching issuer(issuer_id).
