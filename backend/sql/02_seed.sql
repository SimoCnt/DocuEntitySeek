BEGIN;

-- ============================================================
-- INITIAL DATABASE SEED
-- ============================================================


INSERT INTO ai_runtime_configs (
    name, version, 
    engine, 
    model_id, 
    model_revision,
    chunk_size, 
    chunk_overlap, 
    batch_size, 
    num_workers, 
    overlap_policy,
    entity_threshold, 
    field_threshold, 
    is_active
)
VALUES (
    'Default GLiNER2', 
    1, 
    'GLINER2', 
    'fastino/gliner2.5-multi-v1', 
    NULL,
    512,
    96, 
    8, 
    0, 
    'allow',
    0.5000, 
    0.5000, 
    TRUE
)
ON CONFLICT (name, version) DO NOTHING;


-- ============================================================
-- 1. PIANI
-- ============================================================

INSERT INTO plans (
    code,
    name,
    daily_analysis_limit,
    custom_schemas_enabled
)
VALUES
    (
        'BASE',
        'Base',
        5,
        FALSE
    ),
    (
        'PREMIUM',
        'Premium',
        NULL,
        TRUE
    )
ON CONFLICT (code)
DO UPDATE SET
    name = EXCLUDED.name,
    daily_analysis_limit = EXCLUDED.daily_analysis_limit,
    custom_schemas_enabled = EXCLUDED.custom_schemas_enabled;


-- ============================================================
-- 2. UTENTE DEMO
-- ============================================================

/*
INSERT INTO users (
    email,
    role,
    plan_code
)
SELECT
    'demo@docuentityseek.local',
    'USER',
    'BASE'
WHERE NOT EXISTS (
    SELECT 1
    FROM users
    WHERE LOWER(email) = LOWER('demo@docuentityseek.local')
);
*/


-- ============================================================
-- 3. SCHEMA BUILT-IN PREDEFINITO: GENERAL_DOCUMENT
-- ============================================================

-- Unico schema predefinito multi-dominio, valido per tutti i piani.
INSERT INTO extraction_schemas (owner_user_id, structure_key, name, domain, is_builtin)
VALUES (NULL, 'general_document', 'Documento generale', 'Generale', TRUE)
ON CONFLICT (structure_key) DO NOTHING;


-- ============================================================
-- 4. VERSIONE 1 DELLO SCHEMA GENERALE
-- ============================================================

INSERT INTO extraction_schema_versions (schema_id, version, is_active)
SELECT
    s.id,
    1,
    NOT EXISTS (
        SELECT 1 FROM extraction_schema_versions v
        WHERE v.schema_id = s.id AND v.is_active = TRUE
    )
FROM extraction_schemas s
WHERE s.structure_key = 'general_document'
  AND s.is_builtin = TRUE
  AND s.owner_user_id IS NULL
  AND s.archived_at IS NULL
  AND NOT EXISTS (
      SELECT 1 FROM extraction_schema_versions v
      WHERE v.schema_id = s.id AND v.version = 1
  );


-- ============================================================
-- 5. DEFINIZIONI NER PREDEFINITE (ESATTAMENTE 10)
-- ============================================================

INSERT INTO entity_definitions (schema_version_id, label, description, color, sort_order)
SELECT v.id, e.label, e.description, e.color, e.sort_order
FROM extraction_schemas s
JOIN extraction_schema_versions v ON v.schema_id = s.id AND v.version = 1
CROSS JOIN (
    VALUES
        ('PERSONA', 'Nome e cognome di una persona', '#FFE5D9', 1),
        ('ORGANIZZAZIONE', 'Aziende, enti, istituzioni, associazioni e altre organizzazioni.', '#DCEBFF', 2),
        ('LOCALITA', 'Luoghi, comuni, città, indirizzi e riferimenti geografici.', '#E1F5E5', 3),
        ('DATA', 'Date, periodi e riferimenti temporali espressi come data.', '#E8DDF8', 4),
        ('ORA', 'Orari e riferimenti temporali puntuali.', '#F7D9EE', 5),
        ('IMPORTO', 'Somme di denaro e altri valori monetari.', '#FFF1B8', 6),
        ('EMAIL', 'Indirizzi di posta elettronica.', '#D9F0F0', 7),
        ('TELEFONO', 'Numeri telefonici e recapiti telefonici.', '#E5E5FF', 8),
        ('URL', 'Indirizzi web e collegamenti Internet.', '#DFF3FF', 9),
        ('IDENTIFICATIVO', 'Codici, numeri di protocollo, matricole e altri identificativi.', '#FCE0B2', 10)
) AS e(label, description, color, sort_order)
WHERE s.structure_key = 'general_document'
  AND s.is_builtin = TRUE
  AND s.owner_user_id IS NULL
  AND s.archived_at IS NULL
ON CONFLICT (schema_version_id, label)
DO UPDATE SET
    description = EXCLUDED.description,
    color = EXCLUDED.color,
    sort_order = EXCLUDED.sort_order;


-- ============================================================
-- 6. CAMPI INFORMATION EXTRACTION PREDEFINITI (ESATTAMENTE 1)
-- ============================================================

INSERT INTO field_definitions (
    schema_version_id, field_key, label, description, data_type, is_required, sort_order
)
SELECT v.id, 'oggetto_principale', 'Oggetto principale',
       'Argomento o oggetto principale.', 'string', FALSE, 1
FROM extraction_schemas s
JOIN extraction_schema_versions v ON v.schema_id = s.id AND v.version = 1
WHERE s.structure_key = 'general_document'
  AND s.is_builtin = TRUE
  AND s.owner_user_id IS NULL
  AND s.archived_at IS NULL
ON CONFLICT (schema_version_id, field_key)
DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    data_type = EXCLUDED.data_type,
    is_required = EXCLUDED.is_required,
    sort_order = EXCLUDED.sort_order;


COMMIT;
