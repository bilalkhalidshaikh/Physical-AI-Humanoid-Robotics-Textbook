-- 002_create_chat_tables.sql
-- Chat session and message tables (FR-012, FR-031, FR-032)

-- Chat sessions table (user_id is TEXT to match users table)
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
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

-- Chat messages table
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

-- Indexes for chat queries
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_active ON chat_sessions(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(session_id, created_at);

-- Trigger for chat_sessions updated_at
DROP TRIGGER IF EXISTS tr_chat_sessions_updated_at ON chat_sessions;
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

DROP TRIGGER IF EXISTS tr_chat_messages_insert ON chat_messages;
CREATE TRIGGER tr_chat_messages_insert AFTER INSERT ON chat_messages
FOR EACH ROW EXECUTE FUNCTION update_session_on_message();
