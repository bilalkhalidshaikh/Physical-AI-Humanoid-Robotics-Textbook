# Research: Interactive RAG Chatbot, Authentication & Localization

**Feature**: 002-chatbot-auth
**Date**: 2025-12-14
**Status**: Complete

---

## Executive Summary

This document consolidates research findings for implementing the RAG chatbot with authentication and localization features. All technology choices are validated and integration patterns are documented.

---

## 1. Authentication (BetterAuth + Hono)

### Decision: BetterAuth with Hono Framework

**Rationale**: BetterAuth provides a modern, TypeScript-first authentication library with built-in OAuth providers, session management, and database adapters. It's specifically designed for serverless environments.

**Alternatives Considered**:
- NextAuth.js - Tightly coupled to Next.js, not ideal for Hono
- Lucia Auth - Good but BetterAuth has better Hono integration
- Custom JWT - More work, security risks with custom implementation

### Key Integration Patterns

```typescript
// auth-server/src/index.ts
import { Hono } from 'hono';
import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';

export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: 'pg' }),
  emailAndPassword: { enabled: true },
  socialProviders: {
    github: { clientId: process.env.GITHUB_CLIENT_ID!, clientSecret: process.env.GITHUB_CLIENT_SECRET! },
    google: { clientId: process.env.GOOGLE_CLIENT_ID!, clientSecret: process.env.GOOGLE_CLIENT_SECRET! },
  },
  user: {
    additionalFields: {
      softwareBackground: { type: 'string', required: false },
      hardwareBackground: { type: 'string', required: false },
      onboardingCompleted: { type: 'boolean', defaultValue: false },
    },
  },
});
```

### OAuth Setup Requirements

| Provider | Console URL | Callback URL Pattern |
|----------|------------|---------------------|
| GitHub | github.com/settings/developers | `{AUTH_URL}/api/auth/callback/github` |
| Google | console.cloud.google.com | `{AUTH_URL}/api/auth/callback/google` |

---

## 2. RAG Pipeline (OpenAI Agents SDK + Qdrant)

### Decision: OpenAI Agents SDK with Qdrant Cloud

**Rationale**: OpenAI Agents SDK provides structured agent workflows with tool calling, while Qdrant offers a production-ready vector database with a generous free tier.

**Alternatives Considered**:
- LangChain - Heavier, more abstraction than needed
- Pinecone - More expensive, similar capabilities
- Chroma - Good for local, Qdrant better for cloud

### Document Chunking Strategy

```python
# Optimal settings for technical documentation
CHUNK_SIZE = 512       # tokens (approx 1000-1200 chars)
CHUNK_OVERLAP = 50     # tokens for context continuity
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions
```

**Chunking Best Practices**:
1. Respect markdown structure (split at headers)
2. Keep code blocks intact when possible
3. Include section heading in each chunk for context
4. Store metadata: source_file, section, chunk_position, file_hash

### RAG Agent Structure

```python
# backend/agent.py
rag_tool = FunctionTool(
    name="search_knowledge_base",
    description="Search Physical AI textbook for relevant content",
    function=search_qdrant,
    parameters={
        "query": {"type": "string"},
        "top_k": {"type": "integer", "default": 5},
        "module_filter": {"type": "string", "optional": True}
    }
)
```

### Qdrant Collection Configuration

```python
client.create_collection(
    collection_name="physical_ai_book",
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small
        distance=Distance.COSINE
    ),
    hnsw_config=HnswConfigDiff(m=16, ef_construct=100)
)
```

---

## 3. Database (Neon Serverless Postgres)

### Decision: Neon Free Tier with Connection Pooling

**Rationale**: Neon provides serverless PostgreSQL with auto-scaling, built-in connection pooling (PgBouncer), and a free tier sufficient for this project.

**Free Tier Limits**:
- Storage: 0.5 GB
- Compute: 191 hours/month
- Auto-suspend after 5 minutes inactivity

### Connection Patterns

**Node.js (Auth Server)**:
```typescript
import { neon } from '@neondatabase/serverless';
const sql = neon(process.env.DATABASE_URL_POOLED!);
```

**Python (RAG Backend)**:
```python
import asyncpg
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=1,
    max_size=5,
    statement_cache_size=0  # Required for pooler
)
```

### Schema Design Summary

| Table | Purpose | Key Fields |
|-------|---------|------------|
| users | User accounts | id, email, name, email_verified |
| user_profiles | Background info | user_id, software_background, hardware_background |
| sessions | Auth sessions | user_id, token, expires_at |
| accounts | OAuth links | user_id, provider, provider_account_id |
| chat_sessions | Conversation threads | user_id, context_type, context_source |
| chat_messages | Individual messages | session_id, role, content, source_references |
| translation_cache | Cached translations | source_path, content_hash, translated_content |
| personalization_cache | Cached personalizations | user_id, source_path, profile_hash |

---

## 4. Frontend (Docusaurus Swizzling)

### Decision: Swizzle Root + Custom Components

**Rationale**: Docusaurus 3 supports component swizzling to extend the theme. We'll swizzle minimal components and add global providers.

### Components to Create/Swizzle

| Component | Approach | Purpose |
|-----------|----------|---------|
| `src/theme/Root.tsx` | Swizzle (wrap) | Add AuthProvider, ChatProvider |
| `src/theme/Navbar/Content/index.tsx` | Swizzle (wrap) | Add Login button |
| `src/components/ChatWidget.tsx` | New component | Floating chat UI |
| `src/components/ChapterToolbar.tsx` | New component | Translate/Personalize buttons |
| `src/components/TextSelectionHandler.tsx` | New component | Selection detection |

### Swizzle Commands

```bash
# Swizzle Root (safest)
npm run swizzle @docusaurus/theme-classic Root -- --wrap

# Swizzle Navbar Content
npm run swizzle @docusaurus/theme-classic Navbar/Content -- --wrap
```

### Text Selection Detection Pattern

```tsx
// src/components/TextSelectionHandler.tsx
useEffect(() => {
  const handleSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim().length > 10) {
      setSelectedText(selection.toString());
      // Show "Ask about this" prompt
    }
  };
  document.addEventListener('mouseup', handleSelection);
  return () => document.removeEventListener('mouseup', handleSelection);
}, []);
```

---

## 5. AI Translation & Personalization

### Decision: GPT-4o for Both Features

**Rationale**: GPT-4o provides excellent multilingual capabilities for Urdu translation and can understand user backgrounds for personalization.

### Translation Prompt Pattern

```python
TRANSLATION_PROMPT = """
Translate the following technical robotics content to Urdu.

Rules:
1. Keep all code blocks, commands, and technical terms in English
2. Translate prose content naturally to Urdu
3. Maintain markdown formatting
4. Keep variable names, function names, and file paths in English

Content to translate:
{content}
"""
```

### Personalization Prompt Pattern

```python
PERSONALIZATION_PROMPT = """
Rewrite this robotics chapter for a reader with this background:
- Software Experience: {software_background}
- Hardware Experience: {hardware_background}

Rules:
1. Reference familiar concepts briefly ("As you know from Python...")
2. Explain unfamiliar concepts in more detail
3. Use analogies from their known domain
4. Maintain technical accuracy
5. Keep code examples intact

Chapter content:
{content}
"""
```

### Caching Strategy

- **Translation**: Cache by (source_path, content_hash, language) - no user dependency
- **Personalization**: Cache by (user_id, source_path, content_hash, profile_hash) - invalidate when profile changes

---

## 6. Environment Variables

```bash
# Auth Server (.env)
DATABASE_URL="postgresql://..."
DATABASE_URL_POOLED="postgresql://...-pooler..."
BETTER_AUTH_SECRET="min-32-char-secret"
BETTER_AUTH_URL="http://localhost:3001"
GITHUB_CLIENT_ID="..."
GITHUB_CLIENT_SECRET="..."
GOOGLE_CLIENT_ID="..."
GOOGLE_CLIENT_SECRET="..."

# RAG Backend (.env)
DATABASE_URL="postgresql://..."
OPENAI_API_KEY="sk-..."
QDRANT_URL="https://xxx.cloud.qdrant.io"
QDRANT_API_KEY="..."
QDRANT_COLLECTION="physical_ai_book"

# Frontend (.env)
REACT_APP_AUTH_URL="http://localhost:3001"
REACT_APP_RAG_URL="http://localhost:8000"
```

---

## 7. Project Structure

```
Physical-AI-Book/
├── auth-server/                 # Node.js/Hono auth server
│   ├── src/
│   │   ├── index.ts            # Hono app entry
│   │   ├── auth.ts             # BetterAuth config
│   │   └── db/
│   │       ├── schema.ts       # Drizzle schema
│   │       └── client.ts       # Neon connection
│   ├── migrations/
│   └── package.json
│
├── backend/                     # Python FastAPI RAG server
│   ├── main.py                 # FastAPI app
│   ├── agent.py                # OpenAI Agent
│   ├── rag_service.py          # RAG logic
│   ├── memory.py               # Conversation memory
│   └── requirements.txt
│
├── scripts/
│   └── ingest.py               # Document ingestion to Qdrant
│
├── src/                        # Docusaurus source
│   ├── components/
│   │   ├── ChatWidget/
│   │   ├── ChapterToolbar/
│   │   ├── AuthModal/
│   │   └── OnboardingForm/
│   ├── theme/
│   │   ├── Root.tsx            # Swizzled with providers
│   │   └── Navbar/
│   │       └── Content/        # Swizzled with auth button
│   ├── lib/
│   │   ├── auth-client.ts      # BetterAuth client
│   │   └── chat-client.ts      # Chat API client
│   └── context/
│       ├── AuthContext.tsx
│       └── ChatContext.tsx
│
├── docs/                       # Textbook content (existing)
└── docusaurus.config.ts
```

---

## 8. API Endpoints Summary

### Auth Server (port 3001)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/*` | ALL | BetterAuth handlers |
| `/api/user/profile` | GET | Get user profile |
| `/api/user/profile` | POST | Update background |
| `/health` | GET | Health check |

### RAG Backend (port 8000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Send chat message |
| `/chat/sessions` | GET | List user sessions |
| `/chat/sessions/{id}` | GET | Get session with messages |
| `/chat/sessions/{id}` | DELETE | Delete session |
| `/translate` | POST | Translate content to Urdu |
| `/personalize` | POST | Personalize chapter |
| `/health` | GET | Health check |

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OpenAI rate limits | Implement exponential backoff, queue requests |
| Qdrant free tier limits | Monitor usage, optimize chunk size |
| Neon cold starts | Use pooled connections, warm-up queries |
| Translation quality | Preserve technical terms, user feedback |
| Session expiry during long reads | Auto-refresh tokens, preserve conversation |

---

## References

- BetterAuth: https://better-auth.com/docs
- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/
- Qdrant: https://qdrant.tech/documentation/
- Neon: https://neon.tech/docs
- Docusaurus Swizzling: https://docusaurus.io/docs/swizzling
