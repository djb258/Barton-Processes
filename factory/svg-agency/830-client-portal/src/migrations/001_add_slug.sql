-- 830 — Add slug column to client table (shared D1 with 810)
-- Run against client-intake-810 D1 database
ALTER TABLE client ADD COLUMN slug TEXT UNIQUE;
CREATE INDEX IF NOT EXISTS idx_client_slug ON client(slug);
