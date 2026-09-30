CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE users (
 id INTEGER PRIMARY KEY, team_id INTEGER NOT NULL REFERENCES teams(id),
 login TEXT NOT NULL UNIQUE, display_name TEXT NOT NULL, password_hash TEXT NOT NULL,
 role TEXT NOT NULL CHECK(role IN ('operator','consultant','supervisor','admin')),
 enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)),
 session_version INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE sessions (id TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
 token_hash TEXT NOT NULL UNIQUE, session_version INTEGER NOT NULL, expires_at TEXT NOT NULL, revoked_at TEXT);
CREATE TABLE dictionaries (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, code TEXT NOT NULL,
 label TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, UNIQUE(kind,code));
CREATE TABLE hospitals (id INTEGER PRIMARY KEY, name TEXT NOT NULL, region_id INTEGER REFERENCES dictionaries(id));
CREATE TABLE consultant_profiles (user_id INTEGER PRIMARY KEY REFERENCES users(id),
 weight INTEGER NOT NULL DEFAULT 1 CHECK(weight BETWEEN 1 AND 10),
 daily_capacity INTEGER NOT NULL DEFAULT 30 CHECK(daily_capacity>0),
 on_duty INTEGER NOT NULL DEFAULT 0 CHECK(on_duty IN (0,1)), last_assigned_at TEXT);
CREATE TABLE consultant_diseases (user_id INTEGER REFERENCES consultant_profiles(user_id),
 disease_id INTEGER REFERENCES dictionaries(id), PRIMARY KEY(user_id,disease_id));
CREATE TABLE consultant_regions (user_id INTEGER REFERENCES consultant_profiles(user_id),
 region_id INTEGER REFERENCES dictionaries(id), PRIMARY KEY(user_id,region_id));
CREATE TABLE leads (
 id INTEGER PRIMARY KEY, lead_no TEXT NOT NULL UNIQUE, team_id INTEGER NOT NULL REFERENCES teams(id),
 created_by INTEGER NOT NULL REFERENCES users(id), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 disease_id INTEGER NOT NULL REFERENCES dictionaries(id), channel_id INTEGER NOT NULL REFERENCES dictionaries(id),
 region_id INTEGER NOT NULL REFERENCES dictionaries(id), wechat_ciphertext BLOB NOT NULL,
 wechat_hmac TEXT NOT NULL, phone_ciphertext BLOB, phone_hmac TEXT, key_version TEXT NOT NULL,
 nickname TEXT, source_account TEXT, source_video TEXT, external_lead_id TEXT,
 intent_summary TEXT, duplicate_of INTEGER REFERENCES leads(id),
 duplicate_state TEXT NOT NULL DEFAULT 'clear' CHECK(duplicate_state IN ('clear','pending','resolved')),
 assigned_to INTEGER REFERENCES users(id), accepted_at TEXT,
 status TEXT NOT NULL DEFAULT 'pending_assignment' CHECK(status IN
 ('pending_assignment','pending_acceptance','accepted','wechat_added','followup_required','booked','arrived','won','invalid')),
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, version INTEGER NOT NULL DEFAULT 1,
 UNIQUE(channel_id,external_lead_id)
);
CREATE INDEX idx_leads_owner ON leads(created_by,created_at);
CREATE INDEX idx_leads_assignee ON leads(assigned_to,status);
CREATE INDEX idx_leads_duplicate ON leads(team_id,wechat_hmac,created_at);
CREATE INDEX idx_leads_phone ON leads(team_id,phone_hmac);
CREATE TABLE assignments (
 id INTEGER PRIMARY KEY, lead_id INTEGER NOT NULL REFERENCES leads(id),
 previous_consultant_id INTEGER REFERENCES users(id), consultant_id INTEGER REFERENCES users(id),
 actor_id INTEGER REFERENCES users(id), kind TEXT NOT NULL CHECK(kind IN ('automatic','manual','reclaim')),
 reason TEXT, rule_snapshot_json TEXT NOT NULL, assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 acceptance_deadline TEXT, accepted_at TEXT, ended_at TEXT,
 CHECK(kind='automatic' OR length(trim(reason))>0 AND reason IS NOT NULL)
);
CREATE UNIQUE INDEX idx_assignment_active ON assignments(lead_id) WHERE ended_at IS NULL;
CREATE TABLE state_events (id INTEGER PRIMARY KEY, lead_id INTEGER NOT NULL REFERENCES leads(id),
 actor_id INTEGER REFERENCES users(id), from_status TEXT, to_status TEXT NOT NULL,
 result_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE followup_tasks (id INTEGER PRIMARY KEY, lead_id INTEGER NOT NULL REFERENCES leads(id),
 owner_id INTEGER NOT NULL REFERENCES users(id), due_at TEXT NOT NULL, completed_at TEXT, result TEXT);
CREATE TABLE consultation_notes (id INTEGER PRIMARY KEY, lead_id INTEGER NOT NULL REFERENCES leads(id),
 author_id INTEGER NOT NULL REFERENCES users(id), content_ciphertext BLOB NOT NULL, key_version TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE appointments (id INTEGER PRIMARY KEY, lead_id INTEGER NOT NULL REFERENCES leads(id),
 hospital_id INTEGER NOT NULL REFERENCES hospitals(id), appointment_at TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled','cancelled','arrived')),
 created_by INTEGER NOT NULL REFERENCES users(id), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE visits (id INTEGER PRIMARY KEY, appointment_id INTEGER REFERENCES appointments(id),
 lead_id INTEGER NOT NULL REFERENCES leads(id), arrived_at TEXT NOT NULL,
 verified_by INTEGER REFERENCES users(id), verified_at TEXT);
CREATE TABLE deals (id INTEGER PRIMARY KEY, lead_id INTEGER NOT NULL REFERENCES leads(id),
 visit_id INTEGER REFERENCES visits(id), project TEXT NOT NULL, amount_cents INTEGER NOT NULL CHECK(amount_cents>=0),
 deal_at TEXT NOT NULL, verified_by INTEGER REFERENCES users(id), verified_at TEXT, external_receipt_id TEXT UNIQUE);
CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, actor_id INTEGER REFERENCES users(id),
 action TEXT NOT NULL, lead_id INTEGER REFERENCES leads(id), request_id TEXT NOT NULL,
 ip TEXT, device TEXT, safe_metadata_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit_logs BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit_logs BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
CREATE TABLE import_jobs (id INTEGER PRIMARY KEY, created_by INTEGER NOT NULL REFERENCES users(id),
 status TEXT NOT NULL DEFAULT 'pending', total_count INTEGER NOT NULL DEFAULT 0,
 success_count INTEGER NOT NULL DEFAULT 0, failed_count INTEGER NOT NULL DEFAULT 0,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE import_rows (id INTEGER PRIMARY KEY, job_id INTEGER NOT NULL REFERENCES import_jobs(id),
 row_number INTEGER NOT NULL, lead_id INTEGER REFERENCES leads(id), error_code TEXT, UNIQUE(job_id,row_number));
CREATE TABLE notifications (id INTEGER PRIMARY KEY, recipient_id INTEGER NOT NULL REFERENCES users(id),
 lead_id INTEGER REFERENCES leads(id), type TEXT NOT NULL, read_at TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE exception_tasks (id INTEGER PRIMARY KEY, lead_id INTEGER NOT NULL REFERENCES leads(id),
 kind TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open', due_at TEXT, resolved_by INTEGER REFERENCES users(id),
 resolution_reason TEXT, resolved_at TEXT);
CREATE TABLE rule_configs (key TEXT PRIMARY KEY, value_json TEXT NOT NULL, updated_by INTEGER REFERENCES users(id),
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
INSERT INTO rule_configs(key,value_json) VALUES
 ('acceptance_timeout_minutes','5'),('first_contact_timeout_minutes','15'),
 ('timezone','"Asia/Shanghai"'),('operator_can_view_deal_amount','false'),
 ('duplicate_policy','{"scope":"team","window":"all_history","action":"supervisor_review","preserve_original_owner":true}');
