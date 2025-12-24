-- 003_create_cache_tables.sql
-- Translation and personalization cache tables (FR-021-FR-030)

-- Translation cache (FR-021-FR-025)
CREATE TABLE IF NOT EXISTS translation_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    target_language TEXT DEFAULT 'ur',
    translated_content TEXT NOT NULL,
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMPTZ,
    UNIQUE(source_path, content_hash, target_language)
);

-- Personalization cache (FR-026-FR-030, user_id is TEXT to match users table)
CREATE TABLE IF NOT EXISTS personalization_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    profile_hash TEXT NOT NULL,
    personalized_content TEXT NOT NULL,
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE(user_id, source_path, content_hash, profile_hash)
);

-- Indexes for cache lookups
CREATE INDEX IF NOT EXISTS idx_translation_cache_lookup ON translation_cache(source_path, content_hash, target_language);
CREATE INDEX IF NOT EXISTS idx_personalization_cache_lookup ON personalization_cache(user_id, source_path, content_hash);
