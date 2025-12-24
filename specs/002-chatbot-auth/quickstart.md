# Quickstart: Interactive RAG Chatbot, Authentication & Localization

**Feature**: 002-chatbot-auth
**Date**: 2025-12-14

This guide helps developers quickly set up and run the feature locally.

---

## Prerequisites

- Node.js 18+ (for auth server and Docusaurus)
- Python 3.10+ (for RAG backend)
- pnpm or npm
- Git

## External Services Setup

### 1. Neon Postgres Database

1. Create account at [neon.tech](https://neon.tech)
2. Create new project: `physical-ai-book`
3. Copy connection strings from dashboard:
   - Direct: `DATABASE_URL`
   - Pooled: `DATABASE_URL_POOLED` (has `-pooler` in hostname)

### 2. Qdrant Cloud

1. Create account at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create free cluster (1GB)
3. Copy:
   - Cluster URL: `QDRANT_URL`
   - API Key: `QDRANT_API_KEY`

### 3. OpenAI API

1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Copy: `OPENAI_API_KEY`

### 4. OAuth Providers

**GitHub:**
1. Go to [github.com/settings/developers](https://github.com/settings/developers)
2. Create new OAuth App
3. Callback URL: `http://localhost:3001/api/auth/callback/github`
4. Copy Client ID and Secret

**Google:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Authorized redirect URI: `http://localhost:3001/api/auth/callback/google`
4. Copy Client ID and Secret

---

## Quick Setup

### Step 1: Clone and Install

```bash
# Clone repository
git clone <repo-url>
cd Physical-AI-Book

# Install Docusaurus dependencies
npm install

# Create auth server
mkdir -p auth-server
cd auth-server
npm init -y
npm install hono @hono/node-server better-auth @neondatabase/serverless drizzle-orm dotenv
npm install -D typescript tsx @types/node drizzle-kit
cd ..

# Create RAG backend
mkdir -p backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn openai qdrant-client asyncpg python-dotenv tiktoken
cd ..
```

### Step 2: Environment Files

**auth-server/.env:**
```bash
DATABASE_URL="postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require"
DATABASE_URL_POOLED="postgresql://user:pass@ep-xxx-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
BETTER_AUTH_SECRET="your-32-char-secret-key-here-min"
BETTER_AUTH_URL="http://localhost:3001"
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
FRONTEND_URL="http://localhost:3000"
```

**backend/.env:**
```bash
DATABASE_URL="postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require"
OPENAI_API_KEY="sk-..."
QDRANT_URL="https://xxx.cloud.qdrant.io"
QDRANT_API_KEY="your-qdrant-api-key"
QDRANT_COLLECTION="physical_ai_book"
```

### Step 3: Database Setup

```bash
cd auth-server

# Run migrations (after creating migration files)
npx drizzle-kit push:pg

cd ..
```

### Step 4: Ingest Documents

```bash
cd backend
source venv/bin/activate

# Run ingestion script
python scripts/ingest.py

cd ..
```

### Step 5: Start Services

**Terminal 1 - Auth Server:**
```bash
cd auth-server
npm run dev  # Runs on port 3001
```

**Terminal 2 - RAG Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 3 - Docusaurus:**
```bash
npm start  # Runs on port 3000
```

---

## Verification Checklist

### Auth Server (http://localhost:3001)

- [ ] `GET /health` returns `{"status": "healthy"}`
- [ ] `POST /api/auth/signup` creates user
- [ ] `POST /api/auth/signin` returns session
- [ ] OAuth redirects work for GitHub/Google

### RAG Backend (http://localhost:8000)

- [ ] `GET /health` shows Qdrant connected
- [ ] `POST /search` returns document chunks
- [ ] `POST /chat` returns AI response with sources

### Frontend (http://localhost:3000)

- [ ] Login/Signup button visible in navbar
- [ ] Chat widget appears on pages
- [ ] Text selection shows "Ask about this" option

---

## Common Issues

### "Connection refused" on auth server
- Check DATABASE_URL is correct
- Ensure Neon project is not paused

### "Qdrant not connected"
- Verify QDRANT_URL and QDRANT_API_KEY
- Check cluster is running on cloud.qdrant.io

### "No documents found" in chat
- Run `python scripts/ingest.py` first
- Check docs/ folder has markdown files

### OAuth callback fails
- Verify callback URLs match exactly in provider settings
- Check GITHUB_CLIENT_ID/SECRET are correct

---

## Development Workflow

1. **Auth changes**: Edit `auth-server/src/`, restart server
2. **RAG changes**: Edit `backend/`, uvicorn auto-reloads
3. **Frontend changes**: Edit `src/`, Docusaurus hot-reloads
4. **Schema changes**: Update `schema.ts`, run `drizzle-kit push:pg`
5. **Content changes**: Run `python scripts/ingest.py --incremental`

---

## Useful Commands

```bash
# Auth server
cd auth-server
npm run dev          # Start development
npm run db:push      # Push schema changes
npm run db:studio    # Open Drizzle Studio

# RAG backend
cd backend
uvicorn main:app --reload --port 8000  # Start with reload
python scripts/ingest.py               # Full ingestion
python scripts/ingest.py --dry-run     # Preview changes

# Frontend
npm start            # Development server
npm run build        # Production build
npm run swizzle      # Swizzle components
```

---

## Next Steps

After quickstart verification:

1. Complete `/sp.tasks` to generate implementation tasks
2. Start with P1 user stories (authentication, basic chat)
3. Add P2 features (translation, personalization)
4. Deploy to production environment
