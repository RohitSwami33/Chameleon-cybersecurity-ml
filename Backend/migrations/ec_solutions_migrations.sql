-- ============================================================
-- Chameleon EC Solutions Database Migrations
-- ============================================================
-- Run these migrations after deploying the EC security fixes.
-- Execute with: psql -d chameleon_db -f ec_solutions_migrations.sql
-- ============================================================

BEGIN;

-- EC-005: Resize user_agent column to prevent truncation
-- Allows storage of full User-Agent strings up to 512 chars
ALTER TABLE beacon_events 
  ALTER COLUMN user_agent TYPE VARCHAR(512);

-- EC-019: Add NaN/Infinity check constraint on reputation_score
-- Prevents score poisoning via invalid float values
ALTER TABLE reputation_scores 
  ADD CONSTRAINT IF NOT EXISTS reputation_score_valid
  CHECK (reputation_score >= 0 AND reputation_score <= 100);

-- EC-024: Add covering indexes for fast dashboard stats
-- Speeds up COUNT(*) queries and time-based filtering
CREATE INDEX IF NOT EXISTS idx_honeypot_logs_timestamp_desc 
  ON honeypot_logs(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_honeypot_logs_attacker_ip 
  ON honeypot_logs(attacker_ip);

-- EC-024: Additional indexes for common queries
CREATE INDEX IF NOT EXISTS idx_honeypot_logs_tenant_timestamp 
  ON honeypot_logs(tenant_id, timestamp DESC);

-- EC-038/039: Indexes for session and cache lookups
CREATE INDEX IF NOT EXISTS idx_tenants_email 
  ON tenants(email);

CREATE INDEX IF NOT EXISTS idx_tenants_api_key 
  ON tenants(api_key);

-- EC-040: Index for beacon events by session
CREATE INDEX IF NOT EXISTS idx_beacon_events_session 
  ON beacon_events(session_id, triggered_at DESC);

COMMIT;

-- ============================================================
-- Verification queries (run after migration)
-- ============================================================
-- Check column type:
-- SELECT column_name, data_type, character_maximum_length 
--   FROM information_schema.columns 
--   WHERE table_name = 'beacon_events' AND column_name = 'user_agent';

-- Check constraints:
-- SELECT conname, pg_get_constraintdef(oid) 
--   FROM pg_constraint 
--   WHERE conrelid = 'reputation_scores'::regclass;

-- Check indexes:
-- SELECT indexname, indexdef 
--   FROM pg_indexes 
--   WHERE tablename = 'honeypot_logs' 
--   ORDER BY indexname;
-- ============================================================
