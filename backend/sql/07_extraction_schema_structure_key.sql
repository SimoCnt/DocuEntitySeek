BEGIN;

ALTER TABLE extraction_schemas
ADD COLUMN structure_key VARCHAR(120);

UPDATE extraction_schemas
SET structure_key = LOWER(REGEXP_REPLACE(TRIM(name), '[^a-zA-Z0-9]+', '_', 'g'))
    || '_'
    || LEFT(REPLACE(id::TEXT, '-', ''), 8)
WHERE structure_key IS NULL;

ALTER TABLE extraction_schemas
ALTER COLUMN structure_key SET NOT NULL;

ALTER TABLE extraction_schemas
ADD CONSTRAINT uq_extraction_schemas_structure_key UNIQUE (structure_key);

ALTER TABLE extraction_schemas
ADD CONSTRAINT ck_extraction_schemas_structure_key CHECK (LENGTH(TRIM(structure_key)) > 0);

COMMIT;