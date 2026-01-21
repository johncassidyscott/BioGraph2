-- Migration: Enforce that no assertion exists without at least one linked evidence at commit time

CREATE OR REPLACE FUNCTION check_assertion_evidence()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM assertion a
        WHERE NOT EXISTS (
            SELECT 1 FROM assertion_evidence ae WHERE ae.assertion_id = a.id
        )
    ) THEN
        RAISE EXCEPTION 'Assertion(s) without evidence detected at commit time.';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS assertion_evidence_enforce ON assertion;

CREATE CONSTRAINT TRIGGER assertion_evidence_enforce
AFTER INSERT OR UPDATE OR DELETE ON assertion
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION check_assertion_evidence();
