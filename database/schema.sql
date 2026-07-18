-- SQLite reference schema. Alembic migrations are authoritative for Member 2.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;

-- Member 1 reference tables -------------------------------------------------

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    customer_type TEXT NOT NULL,
    business_type TEXT,
    declared_income NUMERIC(18, 2),
    declared_turnover NUMERIC(18, 2),
    country TEXT NOT NULL,
    kyc_status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    account_type TEXT NOT NULL,
    status TEXT NOT NULL,
    opened_at TEXT NOT NULL
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
    occurred_at TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS financial_twins (
    twin_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    profile_json TEXT NOT NULL CHECK (json_valid(profile_json)),
    version INTEGER NOT NULL CHECK (version > 0),
    trust_score NUMERIC(5, 4) NOT NULL CHECK (trust_score BETWEEN 0 AND 1),
    last_updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (customer_id, version)
);

-- Member 2 compliance tables -----------------------------------------------

CREATE TABLE IF NOT EXISTS risk_cases (
    case_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    risk_score REAL NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    risk_level TEXT NOT NULL,
    status TEXT NOT NULL,
    priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 5),
    anomalies TEXT NOT NULL DEFAULT '[]' CHECK (json_valid(anomalies)),
    decision_critical_evidence TEXT CHECK (
        decision_critical_evidence IS NULL OR json_valid(decision_critical_evidence)
    ),
    recommended_actions TEXT NOT NULL DEFAULT '[]' CHECK (json_valid(recommended_actions)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES risk_cases(case_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('LEGITIMATE', 'SUSPICIOUS', 'UNCERTAIN')),
    description TEXT,
    match_score REAL NOT NULL CHECK (match_score BETWEEN 0 AND 100)
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES risk_cases(case_id) ON DELETE CASCADE,
    scenario_id TEXT REFERENCES scenarios(scenario_id) ON DELETE SET NULL,
    evidence_type TEXT NOT NULL,
    description TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('VERIFIED', 'UNVERIFIED', 'CONTRADICTED', 'MISSING')),
    confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    submitted_by TEXT NOT NULL,
    verification_reason TEXT,
    verified_by TEXT,
    verified_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES risk_cases(case_id) ON DELETE CASCADE,
    customer_id TEXT NOT NULL,
    document_type TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    sha256 CHAR(64) NOT NULL,
    size_bytes BIGINT NOT NULL CHECK (size_bytes >= 0),
    extracted_data TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(extracted_data)),
    index_entries TEXT NOT NULL DEFAULT '[]' CHECK (json_valid(index_entries)),
    verification_status TEXT NOT NULL,
    uploaded_by TEXT NOT NULL,
    verified_by TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES risk_cases(case_id) ON DELETE CASCADE,
    reviewer_id TEXT NOT NULL,
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    previous_status TEXT NOT NULL,
    resulting_status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compliance_reports (
    report_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES risk_cases(case_id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    narrative TEXT NOT NULL,
    structured_report TEXT NOT NULL CHECK (json_valid(structured_report)),
    html_path TEXT NOT NULL,
    pdf_path TEXT,
    generated_by TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id TEXT PRIMARY KEY,
    case_id TEXT,
    actor_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(metadata_json)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_customer_time
    ON transactions (customer_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_risk_cases_queue
    ON risk_cases (status, priority, risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_case
    ON evidence (case_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_documents_case
    ON documents (case_id, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_case
    ON audit_logs (case_id, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity
    ON audit_logs (entity_type, entity_id, created_at);
