BEGIN;

-- ============================================================
-- INITIAL DATABASE SEED
-- ============================================================


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


-- ============================================================
-- 3. SCHEMA PREDEFINITO PROCUREMENT
-- ============================================================

INSERT INTO extraction_schemas (
    owner_user_id,
    name,
    domain,
    is_builtin
)
SELECT
    NULL,
    'Procurement',
    'Public Procurement',
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM extraction_schemas
    WHERE owner_user_id IS NULL
      AND LOWER(name) = 'procurement'
);


-- ============================================================
-- 4. VERSIONE 1 DELLO SCHEMA PROCUREMENT
-- ============================================================

INSERT INTO extraction_schema_versions (
    schema_id,
    version,
    is_active
)
SELECT
    s.id,
    1,
    NOT EXISTS (
        SELECT 1
        FROM extraction_schema_versions AS existing
        WHERE existing.schema_id = s.id
          AND existing.is_active = TRUE
    )
FROM extraction_schemas AS s
WHERE s.is_builtin = TRUE
  AND s.owner_user_id IS NULL
  AND LOWER(s.name) = 'procurement'
  AND NOT EXISTS (
      SELECT 1
      FROM extraction_schema_versions AS existing_version
      WHERE existing_version.schema_id = s.id
        AND existing_version.version = 1
  );


-- ============================================================
-- 5. DEFINIZIONI DELLE ENTITÀ NER
-- ============================================================

INSERT INTO entity_definitions (
    schema_version_id,
    label,
    description,
    color,
    sort_order
)
SELECT
    v.id,
    e.label,
    e.description,
    e.color,
    e.sort_order
FROM extraction_schemas AS s

JOIN extraction_schema_versions AS v
    ON v.schema_id = s.id
   AND v.version = 1

CROSS JOIN (
    VALUES
        (
            'ORGANIZZAZIONE',
            'Enti pubblici, amministrazioni, aziende e altre organizzazioni.',
            '#DCEBFF',
            1
        ),
        (
            'PERSONA',
            'Persone fisiche citate nel documento.',
            '#FFE5D9',
            2
        ),
        (
            'LOCALITA',
            'Luoghi, indirizzi e riferimenti geografici.',
            '#E1F5E5',
            3
        ),
        (
            'IMPORTO',
            'Somme di denaro, valori economici e importi monetari.',
            '#FFF1B8',
            4
        ),
        (
            'DATA',
            'Date e scadenze espresse nel documento.',
            '#E8DDF8',
            5
        ),
        (
            'ORA',
            'Orari, ore e indicazioni temporali puntuali.',
            '#F7D9EE',
            6
        ),
        (
            'RIFERIMENTO_NORMATIVO',
            'Leggi, decreti, regolamenti e riferimenti normativi.',
            '#D9F0F0',
            7
        ),
        (
            'IDENTIFICATIVO_GARA',
            'Codici identificativi delle procedure, inclusi CIG, CUP e CPV.',
            '#FCE0B2',
            8
        ),
        (
            'CERTIFICAZIONE',
            'Certificazioni, attestazioni e qualificazioni richieste.',
            '#E5E5FF',
            9
        ),
        (
            'PRODOTTO_SERVIZIO',
            'Prodotti, servizi, forniture e prestazioni oggetto della procedura.',
            '#DFF3FF',
            10
        )
) AS e(
    label,
    description,
    color,
    sort_order
)

WHERE s.is_builtin = TRUE
  AND s.owner_user_id IS NULL
  AND LOWER(s.name) = 'procurement'

ON CONFLICT (
    schema_version_id,
    label
)
DO UPDATE SET
    description = EXCLUDED.description,
    color = EXCLUDED.color,
    sort_order = EXCLUDED.sort_order;


-- ============================================================
-- 6. DEFINIZIONI DEI CAMPI STRUTTURATI
-- ============================================================

INSERT INTO field_definitions (
    schema_version_id,
    field_key,
    label,
    description,
    data_type,
    sort_order
)
SELECT
    v.id,
    f.field_key,
    f.label,
    f.description,
    'string',
    f.sort_order
FROM extraction_schemas AS s

JOIN extraction_schema_versions AS v
    ON v.schema_id = s.id
   AND v.version = 1

CROSS JOIN (
    VALUES
        (
            'stazione_appaltante',
            'Stazione appaltante',
            'Ente che indice o gestisce la procedura',
            1
        ),
        (
            'oggetto_gara',
            'Oggetto gara',
            'Oggetto principale della procedura',
            2
        ),
        (
            'cig',
            'CIG',
            'Codice Identificativo Gara',
            3
        ),
        (
            'cup',
            'CUP',
            'Codice Unico di Progetto',
            4
        ),
        (
            'cpv',
            'CPV',
            'Codice CPV principale',
            5
        ),
        (
            'tipo_procedura',
            'Tipo procedura',
            'Tipo di procedura di affidamento',
            6
        ),
        (
            'importo_complessivo',
            'Importo complessivo',
            'Valore complessivo della procedura',
            7
        ),
        (
            'importo_base_asta',
            'Importo base asta',
            'Importo posto a base di gara',
            8
        ),
        (
            'numero_lotti',
            'Numero lotti',
            'Numero dei lotti previsti dalla procedura',
            9
        ),
        (
            'durata_contratto',
            'Durata contratto',
            'Durata prevista del contratto o dell''affidamento',
            10
        ),
        (
            'scadenza_offerte',
            'Scadenza offerte',
            'Termine ultimo per la presentazione delle offerte',
            11
        ),
        (
            'termine_chiarimenti',
            'Termine chiarimenti',
            'Termine ultimo per richiedere chiarimenti',
            12
        ),
        (
            'criterio_aggiudicazione',
            'Criterio aggiudicazione',
            'Criterio utilizzato per l''aggiudicazione della procedura',
            13
        ),
        (
            'responsabile_procedimento',
            'Responsabile procedimento',
            'Persona responsabile della procedura',
            14
        ),
        (
            'luogo_esecuzione',
            'Luogo esecuzione',
            'Luogo previsto per l''esecuzione del contratto',
            15
        )
) AS f(
    field_key,
    label,
    description,
    sort_order
)

WHERE s.is_builtin = TRUE
  AND s.owner_user_id IS NULL
  AND LOWER(s.name) = 'procurement'

ON CONFLICT (
    schema_version_id,
    field_key
)
DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    data_type = EXCLUDED.data_type,
    sort_order = EXCLUDED.sort_order;


COMMIT;