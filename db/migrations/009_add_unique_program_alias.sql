-- Migration: Add unique constraint on (program_id, alias) for idempotent upsert
ALTER TABLE program_alias
ADD CONSTRAINT program_alias_program_id_alias_key UNIQUE (program_id, alias);