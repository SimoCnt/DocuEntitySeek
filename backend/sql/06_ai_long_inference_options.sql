BEGIN;

ALTER TABLE ai_runtime_configs
ADD COLUMN batch_size INTEGER NOT NULL DEFAULT 8;

ALTER TABLE ai_runtime_configs
ADD COLUMN num_workers INTEGER NOT NULL DEFAULT 0;

ALTER TABLE ai_runtime_configs
ADD COLUMN overlap_policy VARCHAR(20) NOT NULL DEFAULT 'allow';

ALTER TABLE ai_runtime_configs
ADD CONSTRAINT ck_ai_runtime_configs_batch_size
CHECK (batch_size > 0);

ALTER TABLE ai_runtime_configs
ADD CONSTRAINT ck_ai_runtime_configs_num_workers
CHECK (num_workers >= 0);

ALTER TABLE ai_runtime_configs
ADD CONSTRAINT ck_ai_runtime_configs_overlap_policy
CHECK (
    overlap_policy IN (
        'allow',
        'nested',
        'flat',
        'disallow',
        'longest'
    )
);

COMMIT;