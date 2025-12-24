---
id: 010
title: Enforce Gemini Flash Free Tier
stage: green
date: 2025-12-17
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: /sp.implement
labels: ["config", "gemini", "free-tier", "model-fix", "openai-endpoint"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/.env.example
  - backend/rag_service.py
  - backend/translation_service.py
  - backend/personalization_service.py
tests:
  - null
---

## Prompt

/sp.implement

CRITICAL FIX: Enforce Gemini 1.5 Flash Configuration

The backend services are crashing because they are attempting to use models (`gpt-4o`, `gemini-2.0`, `gemini-1.5-pro`) that are either invalid or quota-limited on the Google Free Tier.

REQUIRED IMPLEMENTATION TASKS:

1.  **Update `backend/rag_service.py`**:
    -   Set `CHAT_MODEL` to `"gemini-1.5-flash"`.
    -   Update `GEMINI_MODEL_VARIANTS` to a single-item list: `["gemini-1.5-flash"]`. Remove all others.
    -   Ensure `OPENAI_BASE_URL` logic handles the `models/` prefix correctly if needed (or ensure the model string includes it).

2.  **Update `backend/translation_service.py`**:
    -   Set `TRANSLATION_MODEL` to `"gemini-1.5-flash"`.
    -   Ensure it loads `OPENAI_BASE_URL` from the environment.
    -   Remove any references to "gpt-4o".

3.  **Update `backend/personalization_service.py`**:
    -   Set `PERSONALIZATION_MODEL` to `"gemini-1.5-flash"`.
    -   Ensure it loads `OPENAI_BASE_URL` from the environment.
    -   Remove any references to "gpt-4o".

4.  **Update `backend/.env.example`**:
    -   Set `OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"`
    -   Set `CHAT_MODEL="gemini-1.5-flash"`

Verify all three services use the exact same working configuration.

## Response snapshot

Updated all backend services to use `gemini-1.5-flash` with the `/openai/` endpoint which handles model naming without the `models/` prefix.

### Configuration Applied

**`backend/.env.example`**
```
OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
CHAT_MODEL="gemini-1.5-flash"
```

**All Backend Services**
| File | Model Constant | Value |
|------|----------------|-------|
| `rag_service.py` | `CHAT_MODEL` | `"gemini-1.5-flash"` |
| `rag_service.py` | `GEMINI_MODEL_VARIANTS` | `["gemini-1.5-flash"]` |
| `rag_service.py` | `EMBEDDING_MODEL` | `"text-embedding-004"` |
| `translation_service.py` | `TRANSLATION_MODEL` | `"gemini-1.5-flash"` |
| `personalization_service.py` | `PERSONALIZATION_MODEL` | `"gemini-1.5-flash"` |

### Key Insight

The `/v1beta/openai/` endpoint provides OpenAI-compatible API access and handles model names **without** the `models/` prefix. This is different from the raw `/v1beta/` endpoint which requires the prefix.

## Outcome

- ✅ Impact: All services now use gemini-1.5-flash with correct endpoint
- 🧪 Tests: Manual testing required - restart backend
- 📁 Files: 4 files modified
- 🔁 Next prompts: Test chat, translation, personalization features
- 🧠 Reflection: Google's /openai/ endpoint is the correct choice for OpenAI SDK compatibility

## Evaluation notes (flywheel)

- Failure modes observed: 429 Quota errors, 404 model not found with models/ prefix
- Graders run and results (PASS/FAIL): Pending verification
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test RAG chat with new config
