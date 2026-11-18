-- 作业5设计稿，目标 MySQL 8.0.16+（CHECK 约束在此前版本不执行）；不含真实个人信息或生产凭据。
-- CHAR(26) 为应用生成的稳定 ULID。所有时间采用 UTC 存储，展示时转换时区。
CREATE TABLE account (
  account_id CHAR(26) PRIMARY KEY,
  login_name VARCHAR(32) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  role_code VARCHAR(32) NOT NULL DEFAULT 'user',
  created_at DATETIME(3) NOT NULL,
  updated_at DATETIME(3) NOT NULL,
  CONSTRAINT ck_account_status CHECK (status IN ('active','disabled')),
  CONSTRAINT ck_account_role CHECK (role_code IN ('user','admin')),
  UNIQUE KEY uk_account_login (login_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE account_capability (
  account_id CHAR(26) NOT NULL,
  capability_code VARCHAR(60) NOT NULL,
  granted_at DATETIME(3) NOT NULL,
  PRIMARY KEY (account_id, capability_code),
  CONSTRAINT fk_cap_account FOREIGN KEY (account_id) REFERENCES account(account_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE organization (
  organization_id CHAR(26) PRIMARY KEY,
  name VARCHAR(300) NOT NULL,
  normalized_name VARCHAR(300) NOT NULL,
  source_scope VARCHAR(100) NULL,
  public_status VARCHAR(16) NOT NULL DEFAULT 'public',
  created_at DATETIME(3) NOT NULL,
  KEY ix_org_name (normalized_name),
  CONSTRAINT ck_org_public CHECK (public_status IN ('public','hidden'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE domain (
  domain_id CHAR(26) PRIMARY KEY,
  parent_id CHAR(26) NULL,
  name VARCHAR(200) NOT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE KEY uk_domain_sibling (parent_id, name),
  KEY ix_domain_parent (parent_id, sort_order),
  CONSTRAINT fk_domain_parent FOREIGN KEY (parent_id) REFERENCES domain(domain_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE scholar (
  scholar_id CHAR(26) PRIMARY KEY,
  display_name VARCHAR(200) NOT NULL,
  aliases_json JSON NULL,
  organization_id CHAR(26) NULL,
  biography TEXT NULL,
  identity_status VARCHAR(20) NOT NULL DEFAULT 'candidate',
  public_status VARCHAR(16) NOT NULL DEFAULT 'public',
  data_nature VARCHAR(16) NOT NULL DEFAULT 'real',
  version BIGINT NOT NULL DEFAULT 1,
  created_at DATETIME(3) NOT NULL,
  updated_at DATETIME(3) NOT NULL,
  KEY ix_scholar_org_public (organization_id, public_status),
  KEY ix_scholar_name (display_name),
  CONSTRAINT fk_scholar_org FOREIGN KEY (organization_id) REFERENCES organization(organization_id),
  CONSTRAINT ck_scholar_identity CHECK (identity_status IN ('candidate','verified','disputed')),
  CONSTRAINT ck_scholar_public CHECK (public_status IN ('public','hidden')),
  CONSTRAINT ck_scholar_nature CHECK (data_nature IN ('real','simulated','mixed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE work (
  work_id CHAR(26) PRIMARY KEY,
  work_type VARCHAR(16) NOT NULL,
  title VARCHAR(1000) NOT NULL,
  abstract_text TEXT NULL,
  publication_year SMALLINT NULL,
  date_precision VARCHAR(8) NULL,
  identifier_kind VARCHAR(32) NULL,
  identifier_scope VARCHAR(100) NULL,
  identifier_norm VARCHAR(300) NULL,
  type_details JSON NOT NULL,
  public_status VARCHAR(16) NOT NULL DEFAULT 'candidate',
  data_nature VARCHAR(16) NOT NULL,
  version BIGINT NOT NULL DEFAULT 1,
  created_at DATETIME(3) NOT NULL,
  updated_at DATETIME(3) NOT NULL,
  KEY ix_work_browse (public_status, work_type, publication_year, work_id),
  KEY ix_work_identifier (identifier_kind, identifier_scope, identifier_norm),
  CONSTRAINT ck_work_type CHECK (work_type IN ('paper','patent','project','award')),
  CONSTRAINT ck_work_public CHECK (public_status IN ('candidate','public','withdrawn','hidden')),
  CONSTRAINT ck_work_nature CHECK (data_nature IN ('real','simulated','mixed')),
  CONSTRAINT ck_work_precision CHECK (date_precision IS NULL OR date_precision IN ('year','month','day')),
  CONSTRAINT ck_work_year CHECK (publication_year IS NULL OR publication_year BETWEEN 1000 AND 9999)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE work_scholar (
  relation_id CHAR(26) PRIMARY KEY,
  work_id CHAR(26) NOT NULL,
  scholar_id CHAR(26) NOT NULL,
  role_code VARCHAR(40) NOT NULL,
  author_order INT NULL,
  organization_at_work_id CHAR(26) NULL,
  confirmation_status VARCHAR(24) NOT NULL,
  evidence_record_id CHAR(26) NULL,
  version BIGINT NOT NULL DEFAULT 1,
  created_at DATETIME(3) NOT NULL,
  UNIQUE KEY uk_work_scholar_role (work_id, scholar_id, role_code),
  KEY ix_ws_scholar (scholar_id, confirmation_status, work_id),
  CONSTRAINT fk_ws_work FOREIGN KEY (work_id) REFERENCES work(work_id),
  CONSTRAINT fk_ws_scholar FOREIGN KEY (scholar_id) REFERENCES scholar(scholar_id),
  CONSTRAINT fk_ws_org FOREIGN KEY (organization_at_work_id) REFERENCES organization(organization_id),
  CONSTRAINT ck_ws_status CHECK (confirmation_status IN ('auto_linked','self_confirmed','pending','disputed','excluded')),
  CONSTRAINT ck_ws_order CHECK (author_order IS NULL OR author_order > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE work_domain (
  work_id CHAR(26) NOT NULL,
  domain_id CHAR(26) NOT NULL,
  PRIMARY KEY (work_id, domain_id),
  KEY ix_wd_domain (domain_id, work_id),
  CONSTRAINT fk_wd_work FOREIGN KEY (work_id) REFERENCES work(work_id),
  CONSTRAINT fk_wd_domain FOREIGN KEY (domain_id) REFERENCES domain(domain_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE scholar_domain (
  scholar_id CHAR(26) NOT NULL,
  domain_id CHAR(26) NOT NULL,
  PRIMARY KEY (scholar_id, domain_id),
  KEY ix_sd_domain (domain_id, scholar_id),
  CONSTRAINT fk_sd_scholar FOREIGN KEY (scholar_id) REFERENCES scholar(scholar_id),
  CONSTRAINT fk_sd_domain FOREIGN KEY (domain_id) REFERENCES domain(domain_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE claim_application (
  claim_id CHAR(26) PRIMARY KEY,
  applicant_account_id CHAR(26) NOT NULL,
  target_scholar_id CHAR(26) NOT NULL,
  declaration_text VARCHAR(1000) NOT NULL,
  evidence_object_keys JSON NOT NULL,
  state VARCHAR(20) NOT NULL DEFAULT 'pending_review',
  review_reason VARCHAR(1000) NULL,
  reviewer_account_id CHAR(26) NULL,
  version BIGINT NOT NULL DEFAULT 1,
  submitted_at DATETIME(3) NOT NULL,
  decided_at DATETIME(3) NULL,
  KEY ix_claim_queue (state, submitted_at, claim_id),
  KEY ix_claim_applicant (applicant_account_id, submitted_at),
  KEY ix_claim_target (target_scholar_id, state),
  CONSTRAINT fk_claim_applicant FOREIGN KEY (applicant_account_id) REFERENCES account(account_id),
  CONSTRAINT fk_claim_target FOREIGN KEY (target_scholar_id) REFERENCES scholar(scholar_id),
  CONSTRAINT fk_claim_reviewer FOREIGN KEY (reviewer_account_id) REFERENCES account(account_id),
  CONSTRAINT ck_claim_state CHECK (state IN ('pending_review','needs_more','approved','rejected'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE portal_grant (
  grant_id CHAR(26) PRIMARY KEY,
  account_id CHAR(26) NOT NULL,
  scholar_id CHAR(26) NOT NULL,
  source_claim_id CHAR(26) NOT NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  granted_at DATETIME(3) NOT NULL,
  revoked_at DATETIME(3) NULL,
  UNIQUE KEY uk_grant_account_scholar (account_id, scholar_id),
  KEY ix_grant_scholar_active (scholar_id, active),
  CONSTRAINT fk_grant_account FOREIGN KEY (account_id) REFERENCES account(account_id),
  CONSTRAINT fk_grant_scholar FOREIGN KEY (scholar_id) REFERENCES scholar(scholar_id),
  CONSTRAINT fk_grant_claim FOREIGN KEY (source_claim_id) REFERENCES claim_application(claim_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE data_source (
  source_id CHAR(26) PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  source_kind VARCHAR(16) NOT NULL,
  license_scope VARCHAR(1000) NOT NULL,
  allowed_work_types JSON NOT NULL,
  rate_limit_per_minute INT NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT FALSE,
  verified_at DATETIME(3) NULL,
  CONSTRAINT ck_source_kind CHECK (source_kind IN ('public_api','approved_file','approved_web')),
  CONSTRAINT ck_source_rate CHECK (rate_limit_per_minute > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE source_record (
  record_id CHAR(26) PRIMARY KEY,
  source_id CHAR(26) NOT NULL,
  external_id VARCHAR(300) NOT NULL,
  work_id CHAR(26) NULL,
  raw_object_key VARCHAR(500) NOT NULL,
  source_updated_at DATETIME(3) NULL,
  collected_at DATETIME(3) NOT NULL,
  allowed_public BOOLEAN NOT NULL DEFAULT FALSE,
  data_nature VARCHAR(16) NOT NULL,
  content_hash CHAR(64) NOT NULL,
  record_version BIGINT NOT NULL DEFAULT 1,
  UNIQUE KEY uk_source_external (source_id, external_id),
  KEY ix_sr_work (work_id),
  KEY ix_sr_source_updated (source_id, source_updated_at),
  CONSTRAINT fk_sr_source FOREIGN KEY (source_id) REFERENCES data_source(source_id),
  CONSTRAINT fk_sr_work FOREIGN KEY (work_id) REFERENCES work(work_id),
  CONSTRAINT ck_sr_nature CHECK (data_nature IN ('real','simulated','mixed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE source_record_history (
  record_id CHAR(26) NOT NULL,
  record_version BIGINT NOT NULL,
  raw_object_key VARCHAR(500) NOT NULL,
  content_hash CHAR(64) NOT NULL,
  source_updated_at DATETIME(3) NULL,
  observed_at DATETIME(3) NOT NULL,
  change_kind VARCHAR(20) NOT NULL,
  PRIMARY KEY (record_id, record_version),
  CONSTRAINT fk_srh_record FOREIGN KEY (record_id) REFERENCES source_record(record_id),
  CONSTRAINT ck_srh_kind CHECK (change_kind IN ('created','changed','withdrawn','invalidated'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE work_scholar ADD CONSTRAINT fk_ws_evidence
  FOREIGN KEY (evidence_record_id) REFERENCES source_record(record_id);

CREATE TABLE collection_task (
  task_id CHAR(26) PRIMARY KEY,
  source_id CHAR(26) NOT NULL,
  created_by CHAR(26) NOT NULL,
  mode_code VARCHAR(16) NOT NULL,
  parameters_json JSON NOT NULL,
  state VARCHAR(16) NOT NULL DEFAULT 'pending',
  checkpoint_json JSON NULL,
  processed_count BIGINT NOT NULL DEFAULT 0,
  success_count BIGINT NOT NULL DEFAULT 0,
  failure_count BIGINT NOT NULL DEFAULT 0,
  retry_count INT NOT NULL DEFAULT 0,
  failure_reason VARCHAR(1000) NULL,
  lease_owner VARCHAR(100) NULL,
  lease_until DATETIME(3) NULL,
  created_at DATETIME(3) NOT NULL,
  started_at DATETIME(3) NULL,
  ended_at DATETIME(3) NULL,
  version BIGINT NOT NULL DEFAULT 1,
  KEY ix_task_queue (state, lease_until, created_at),
  KEY ix_task_source (source_id, created_at),
  CONSTRAINT fk_task_source FOREIGN KEY (source_id) REFERENCES data_source(source_id),
  CONSTRAINT fk_task_creator FOREIGN KEY (created_by) REFERENCES account(account_id),
  CONSTRAINT ck_task_state CHECK (state IN ('pending','running','succeeded','failed','stopped','retrying')),
  CONSTRAINT ck_task_counts CHECK (processed_count >= 0 AND success_count >= 0 AND failure_count >= 0 AND retry_count >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE audit_log (
  audit_id CHAR(26) PRIMARY KEY,
  actor_account_id CHAR(26) NULL,
  action_code VARCHAR(80) NOT NULL,
  object_type VARCHAR(40) NOT NULL,
  object_id CHAR(26) NOT NULL,
  before_summary JSON NULL,
  after_summary JSON NULL,
  reason VARCHAR(1000) NULL,
  outcome VARCHAR(16) NOT NULL,
  happened_at DATETIME(3) NOT NULL,
  correlation_id CHAR(26) NULL,
  KEY ix_audit_object (object_type, object_id, happened_at),
  KEY ix_audit_actor (actor_account_id, happened_at),
  CONSTRAINT fk_audit_actor FOREIGN KEY (actor_account_id) REFERENCES account(account_id),
  CONSTRAINT ck_audit_outcome CHECK (outcome IN ('success','rejected','failed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE outbox_event (
  event_id CHAR(26) PRIMARY KEY,
  aggregate_type VARCHAR(40) NOT NULL,
  aggregate_id CHAR(26) NOT NULL,
  aggregate_version BIGINT NOT NULL,
  event_type VARCHAR(80) NOT NULL,
  payload_json JSON NOT NULL,
  state VARCHAR(16) NOT NULL DEFAULT 'pending',
  attempt_count INT NOT NULL DEFAULT 0,
  available_at DATETIME(3) NOT NULL,
  created_at DATETIME(3) NOT NULL,
  delivered_at DATETIME(3) NULL,
  UNIQUE KEY uk_outbox_aggregate (aggregate_type, aggregate_id, aggregate_version, event_type),
  KEY ix_outbox_queue (state, available_at, created_at),
  CONSTRAINT ck_outbox_state CHECK (state IN ('pending','delivered','failed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
