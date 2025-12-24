# Data Model: Interactive RAG Chatbot, Authentication & Localization

**Feature**: 002-chatbot-auth
**Date**: 2025-12-14
**Database**: Neon Serverless Postgres + Qdrant Cloud

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────┐
│     users       │───────│   user_profiles  │
└─────────────────┘  1:1  └──────────────────┘
        │
        │ 1:N
        ▼
┌─────────────────┐       ┌──────────────────┐
│    accounts     │       │    sessions      │
└─────────────────┘       └──────────────────┘
        │
        │
        ▼
┌─────────────────┐       ┌──────────────────┐
│  chat_sessions  │───────│  chat_messages   │
└─────────────────┘  1:N  └──────────────────┘
        │
        │ 1:N
        ▼
┌─────────────────────────┐
│  personalization_cache  │
└─────────────────────────┘

┌─────────────────────────┐
│   translation_cache     │  (no user relation)
└─────────────────────────┘

[Qdrant Vector DB]
┌─────────────────────────┐
│    document_chunks      │
└─────────────────────────┘
```

---

## PostgreSQL Tables

### 1. users

Core user account table (BetterAuth compatible).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Unique identifier |
| email | TEXT | NOT NULL, UNIQUE | User email address |
| name | TEXT | NULLABLE | Display name |
| email_verified | BOOLEAN | DEFAULT FALSE | Email verification status |
| image | TEXT | NULLABLE | Profile image URL |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update time |

**Indexes**:
- `idx_users_email` ON email

---

### 2. user_profiles

Extended user information for personalization (FR-005, FR-006).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Unique identifier |
| user_id | UUID | FK → users(id) ON DELETE CASCADE, UNIQUE | Parent user |
| software_background | TEXT | NULLABLE | User's software experience |
| hardware_background | TEXT | NULLABLE | User's hardware experience |
| background_summary | TEXT | NULLABLE | AI-generated summary |
| preferred_language | TEXT | DEFAULT 'en', CHECK IN ('en', 'ur') | Language preference |
| personalization_enabled | BOOLEAN | DEFAULT TRUE | Enable personalization |
| onboarding_completed | BOOLEAN | DEFAULT FALSE | Onboarding status |
| onboarding_completed_at | TIMESTAMPTZ | NULLABLE | When onboarding was completed |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update time |

**Validation Rules**:
- `software_background` + `hardware_background` combined max 5000 chars
- `onboarding_completed_at` set when `onboarding_completed` becomes TRUE

---

### 3. sessions

Authentication sessions (BetterAuth compatible, FR-007).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Session ID |
| user_id | UUID | FK → users(id) ON DELETE CASCADE | Session owner |
| token | TEXT | NOT NULL, UNIQUE | Session token |
| expires_at | TIMESTAMPTZ | NOT NULL | Expiration time |
| ip_address | TEXT | NULLABLE | Client IP |
| user_agent | TEXT | NULLABLE | Client user agent |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Session start |

**Indexes**:
- `idx_sessions_user_id` ON user_id
- `idx_sessions_token` ON token
- `idx_sessions_expires` ON expires_at

**State Transitions**:
- Created on login → Active
- Expired (expires_at < NOW()) → Invalid (auto-cleanup)
- User logout → Deleted

---

### 4. accounts

OAuth provider accounts (BetterAuth compatible, FR-003, FR-004).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Account ID |
| user_id | UUID | FK → users(id) ON DELETE CASCADE | Account owner |
| provider | TEXT | NOT NULL | Provider name: 'github', 'google', 'email' |
| provider_account_id | TEXT | NOT NULL | ID from provider |
| access_token | TEXT | NULLABLE | OAuth access token |
| refresh_token | TEXT | NULLABLE | OAuth refresh token |
| expires_at | TIMESTAMPTZ | NULLABLE | Token expiration |
| token_type | TEXT | NULLABLE | Token type |
| scope | TEXT | NULLABLE | Granted scopes |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Link creation time |

**Constraints**:
- UNIQUE(provider, provider_account_id)

**Indexes**:
- `idx_accounts_user_id` ON user_id
- `idx_accounts_provider` ON (provider, provider_account_id)

---

### 5. chat_sessions

Conversation threads for RAG chatbot (FR-012, FR-031).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Session ID |
| user_id | UUID | FK → users(id) ON DELETE CASCADE, NULLABLE | Session owner (NULL for anonymous) |
| title | TEXT | NULLABLE | Auto-generated title |
| context_type | TEXT | DEFAULT 'general', CHECK IN ('general', 'selection', 'chapter') | Context mode |
| context_source | TEXT | NULLABLE | File path or selected text |
| context_metadata | JSONB | DEFAULT '{}' | Additional context |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| message_count | INTEGER | DEFAULT 0 | Message counter |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last activity |
| last_message_at | TIMESTAMPTZ | NULLABLE | Last message time |

**Context Types** (FR-016-FR-020):
- `general`: Query entire book corpus
- `selection`: Query specific highlighted text
- `chapter`: Query specific chapter/document

**Indexes**:
- `idx_chat_sessions_user_id` ON user_id
- `idx_chat_sessions_updated` ON updated_at DESC
- `idx_chat_sessions_active` ON (user_id, is_active) WHERE is_active = TRUE

---

### 6. chat_messages

Individual messages within chat sessions (FR-031, FR-032).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Message ID |
| session_id | UUID | FK → chat_sessions(id) ON DELETE CASCADE | Parent session |
| role | TEXT | NOT NULL, CHECK IN ('user', 'assistant', 'system') | Message role |
| content | TEXT | NOT NULL | Message content |
| source_references | JSONB | DEFAULT '[]' | RAG source citations |
| prompt_tokens | INTEGER | NULLABLE | Tokens in prompt |
| completion_tokens | INTEGER | NULLABLE | Tokens in completion |
| metadata | JSONB | DEFAULT '{}' | Model info, latency, etc. |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Message time |

**source_references Schema**:
```json
[
  {
    "file": "docs/module-1-ros2/basics.md",
    "section": "Getting Started",
    "chunk_id": "abc123",
    "score": 0.89
  }
]
```

**Indexes**:
- `idx_chat_messages_session` ON session_id
- `idx_chat_messages_created` ON (session_id, created_at)

---

### 7. translation_cache

Cached Urdu translations (FR-021-FR-025).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Cache entry ID |
| source_path | TEXT | NOT NULL | Source file path |
| content_hash | TEXT | NOT NULL | MD5 hash of original |
| target_language | TEXT | DEFAULT 'ur' | Target language |
| translated_content | TEXT | NOT NULL | Translated text |
| model_version | TEXT | NULLABLE | GPT model used |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Cache time |
| expires_at | TIMESTAMPTZ | NULLABLE | Optional TTL |

**Constraints**:
- UNIQUE(source_path, content_hash, target_language)

**Indexes**:
- `idx_translation_cache_lookup` ON (source_path, content_hash, target_language)

---

### 8. personalization_cache

Cached personalized content (FR-026-FR-030).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Cache entry ID |
| user_id | UUID | FK → users(id) ON DELETE CASCADE | Cache owner |
| source_path | TEXT | NOT NULL | Source file path |
| content_hash | TEXT | NOT NULL | MD5 of original |
| profile_hash | TEXT | NOT NULL | MD5 of user background |
| personalized_content | TEXT | NOT NULL | Personalized text |
| model_version | TEXT | NULLABLE | GPT model used |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Cache time |

**Constraints**:
- UNIQUE(user_id, source_path, content_hash, profile_hash)

**Indexes**:
- `idx_personalization_cache_lookup` ON (user_id, source_path, content_hash)

**Cache Invalidation**:
- Invalidate when user profile (background) changes
- Invalidate when source content changes (content_hash mismatch)

---

## Qdrant Vector Database

### Collection: physical_ai_book

Stores document embeddings for RAG retrieval (FR-013, FR-014).

**Vector Configuration**:
```python
VectorParams(
    size=1536,  # text-embedding-3-small dimensions
    distance=Distance.COSINE
)
```

**Payload Schema** (per point):

| Field | Type | Description |
|-------|------|-------------|
| text | string | Chunk text content |
| source_file | string | Relative path: "module-1-ros2/basics.md" |
| section | string | Section heading |
| chunk_position | integer | 0-indexed position in file |
| file_hash | string | MD5 of source file |
| last_modified | string | ISO timestamp |
| chapter | string | Top-level chapter name |
| module | string | Module identifier: "ros2", "gazebo", "isaac_sim", "vla" |
| doc_type | string | "tutorial", "reference", "concept" |
| has_code | boolean | Contains code blocks |
| word_count | integer | Word count in chunk |

**Payload Indexes**:
- `source_file`: KEYWORD (for filtering by document)
- `section`: TEXT (for section search)
- `chunk_position`: INTEGER (for ordering)
- `file_hash`: KEYWORD (for incremental updates)
- `module`: KEYWORD (for module filtering)

---

## SQL Migration Scripts

### Migration 001: Core Tables

```sql
-- 001_create_core_tables.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    image TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    software_background TEXT,
    hardware_background TEXT,
    background_summary TEXT,
    preferred_language TEXT DEFAULT 'en' CHECK (preferred_language IN ('en', 'ur')),
    personalization_enabled BOOLEAN DEFAULT TRUE,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    provider_account_id TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMPTZ,
    token_type TEXT,
    scope TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE(provider, provider_account_id)
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_provider ON accounts(provider, provider_account_id);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_user_profiles_updated_at BEFORE UPDATE ON user_profiles
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### Migration 002: Chat Tables

```sql
-- 002_create_chat_tables.sql

CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    context_type TEXT DEFAULT 'general' CHECK (context_type IN ('general', 'selection', 'chapter')),
    context_source TEXT,
    context_metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    last_message_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    source_references JSONB DEFAULT '[]',
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_updated ON chat_sessions(updated_at DESC);
CREATE INDEX idx_chat_sessions_active ON chat_sessions(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created ON chat_messages(session_id, created_at);

-- Trigger for updated_at
CREATE TRIGGER tr_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Trigger to update session stats on message insert
CREATE OR REPLACE FUNCTION update_session_on_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions
    SET message_count = message_count + 1,
        last_message_at = NEW.created_at,
        updated_at = NOW()
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_chat_messages_insert AFTER INSERT ON chat_messages
FOR EACH ROW EXECUTE FUNCTION update_session_on_message();
```

### Migration 003: Cache Tables

```sql
-- 003_create_cache_tables.sql

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

CREATE TABLE IF NOT EXISTS personalization_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    profile_hash TEXT NOT NULL,
    personalized_content TEXT NOT NULL,
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE(user_id, source_path, content_hash, profile_hash)
);

-- Indexes
CREATE INDEX idx_translation_cache_lookup ON translation_cache(source_path, content_hash, target_language);
CREATE INDEX idx_personalization_cache_lookup ON personalization_cache(user_id, source_path, content_hash);
```

---

## Data Retention & Cleanup

| Data Type | Retention | Cleanup Method |
|-----------|-----------|----------------|
| User accounts | Until deleted | CASCADE on delete |
| Sessions | Until expiry | Cron: DELETE WHERE expires_at < NOW() |
| Chat history | Indefinite | User-initiated deletion |
| Translation cache | 30 days | Cron: DELETE WHERE created_at < NOW() - INTERVAL '30 days' |
| Personalization cache | Until profile change | Trigger on profile update |
| Qdrant embeddings | Until source update | Incremental re-ingestion |
