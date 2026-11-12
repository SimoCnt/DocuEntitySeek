BEGIN;


-- ============================================================
-- AUTHENTICATION COLUMNS
-- ============================================================

ALTER TABLE users
ADD COLUMN password_hash TEXT;

ALTER TABLE users
ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE users
ADD COLUMN last_login_at TIMESTAMPTZ;


-- ============================================================
-- LEGACY DEVELOPMENT USERS
-- Gli utenti esistenti sono stati creati prima dell'introduzione dell'autenticazione e non possiedono quindi una password valida.
-- ============================================================

UPDATE users
SET is_active = FALSE
WHERE password_hash IS NULL;


-- ============================================================
-- ACTIVE USERS MUST HAVE A PASSWORD
-- ============================================================

ALTER TABLE users
ADD CONSTRAINT ck_users_active_password
CHECK (
    is_active = FALSE
    OR password_hash IS NOT NULL
);


COMMIT;