# API Contracts: Interactive RAG Chatbot, Authentication & Localization

**Feature**: 002-chatbot-auth
**Date**: 2025-12-14

This directory contains API contract specifications for the feature.

## Servers

| Server | Port | Technology | Purpose |
|--------|------|------------|---------|
| Auth Server | 3001 | Node.js/Hono + BetterAuth | Authentication & user profiles |
| RAG Backend | 8000 | Python/FastAPI | Chat, translation, personalization |

## Contract Files

- `auth-api.yaml` - OpenAPI spec for auth server
- `rag-api.yaml` - OpenAPI spec for RAG backend

## Authentication Flow

```
Frontend                Auth Server              Database
   │                        │                       │
   │  POST /api/auth/signup │                       │
   │───────────────────────>│                       │
   │                        │   INSERT user         │
   │                        │──────────────────────>│
   │                        │                       │
   │   Set-Cookie: session  │                       │
   │<───────────────────────│                       │
   │                        │                       │
   │  GET /api/user/profile │                       │
   │───────────────────────>│                       │
   │                        │   SELECT profile      │
   │                        │──────────────────────>│
   │                        │                       │
   │   { profile data }     │                       │
   │<───────────────────────│                       │
```

## Chat Flow

```
Frontend              RAG Backend               Qdrant          OpenAI
   │                      │                       │                │
   │  POST /chat          │                       │                │
   │─────────────────────>│                       │                │
   │                      │   embed(query)        │                │
   │                      │───────────────────────────────────────>│
   │                      │                       │                │
   │                      │   search(vector)      │                │
   │                      │──────────────────────>│                │
   │                      │   [relevant chunks]   │                │
   │                      │<──────────────────────│                │
   │                      │                       │                │
   │                      │   chat.completions    │                │
   │                      │───────────────────────────────────────>│
   │                      │                       │                │
   │  { response, sources }                       │                │
   │<─────────────────────│                       │                │
```
