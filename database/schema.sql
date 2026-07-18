-- PostgreSQL-oriented baseline schema. Alembic owns subsequent schema evolution.

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    customer_type TEXT NOT NULL,
    business_type TEXT,
    declared_income NUMERIC(18, 2),
    declared_turnover NUMERIC(18, 2),
    country TEXT NOT NULL,
    kyc_status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    account_type TEXT NOT NULL,
    status TEXT NOT NULL,
    opened_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    source_account_id TEXT NOT NULL,
    destination_account_id TEXT NOT NULL,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    amount NUMERIC(18, 2) NOT NULL CHECK (amount >= 0),
    currency CHAR(3) NOT NULL,
    direction TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    channel TEXT NOT NULL,
    country TEXT NOT NULL,
    beneficiary_id TEXT,
    device_id TEXT,
    occurred_at TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS financial_twins (
    twin_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    profile_json JSONB NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    trust_score NUMERIC(5, 4) NOT NULL CHECK (trust_score BETWEEN 0 AND 1),
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (customer_id, version)
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    document_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    extracted_data_json JSONB,
    verification_status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_cases (
    case_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    trigger_transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id),
    initial_anomaly_score NUMERIC(5, 2) NOT NULL CHECK (initial_anomaly_score BETWEEN 0 AND 100),
    current_risk_score NUMERIC(5, 2) NOT NULL CHECK (current_risk_score BETWEEN 0 AND 100),
    risk_level TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES risk_cases(case_id),
    category TEXT NOT NULL CHECK (category IN ('LEGITIMATE', 'SUSPICIOUS', 'UNCERTAIN')),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    expected_signals_json JSONB NOT NULL,
    match_score NUMERIC(5, 4) CHECK (match_score BETWEEN 0 AND 1)
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES risk_cases(case_id),
    scenario_id TEXT REFERENCES scenarios(scenario_id),
    evidence_type TEXT NOT NULL,
    description TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence NUMERIC(5, 4) NOT NULL CHECK (confidence BETWEEN 0 AND 1)
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES risk_cases(case_id),
    reviewer_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id TEXT PRIMARY KEY,
    actor_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_customer_time
    ON transactions (customer_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_risk_cases_status
    ON risk_cases (status, current_risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity
    ON audit_logs (entity_type, entity_id, created_at);
