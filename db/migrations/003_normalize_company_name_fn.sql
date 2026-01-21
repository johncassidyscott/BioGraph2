-- normalize_company_name SQL function for use in queries
CREATE OR REPLACE FUNCTION normalize_company_name(text TEXT)
RETURNS TEXT AS $$
DECLARE
    t TEXT := UPPER(text);
BEGIN
    -- Remove punctuation
    t := regexp_replace(t, '[\.,;:/\\\-''"&()\[\]{}]', ' ', 'g');
    -- Collapse whitespace
    t := regexp_replace(t, '\s+', ' ', 'g');
    t := trim(t);
    -- Remove corporate suffixes
    FOR suffix IN ARRAY [' INC', ' INCORPORATED', ' LLC', ' LTD', ' LIMITED', ' CORP', ' CORPORATION',
                        ' CO', ' COMPANY', ' PLC', ' LP', ' SA', ' BV', ' NV', ' GMBH', ' AG', ' SPA',
                        ' SARL', ' AB', ' OYJ', ' KK', ' PTY']
    LOOP
        IF right(t, length(suffix)) = suffix THEN
            t := left(t, length(t) - length(suffix));
            t := trim(t);
        END IF;
    END LOOP;
    RETURN t;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
