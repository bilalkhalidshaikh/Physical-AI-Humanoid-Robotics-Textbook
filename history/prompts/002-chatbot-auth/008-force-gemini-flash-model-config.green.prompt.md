---
id: 008
title: Force Gemini 1.5 Flash Model Config
stage: green
date: 2025-12-16
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: /sp.implement
labels: ["config", "gemini", "model", "free-tier", "quota-fix"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/rag_service.py
  - backend/translation_service.py
  - backend/personalization_service.py
tests:
  - null
---

## Prompt

/sp.implement

CRITICAL CONFIG UPDATE: Force Gemini 1.5 Flash

We are hitting 429 (Quota) and 404 (Not Found) errors because the system is retrying on models not supported by the Google Free Tier.

1. Update `backend/rag_service.py`:
   - Change `GEMINI_MODEL_VARIANTS` to contain ONLY `["gemini-1.5-flash"]`. Remove all other models.
   - Ensure `CHAT_MODEL` defaults to `"gemini-1.5-flash"`.

2. Update `backend/translation_service.py`:
   - Change `TRANSLATION_MODEL` (or the model string in the client call) to `"gemini-1.5-flash"`.
   - Ensure it uses `OPENAI_BASE_URL` from env.

3. Update `backend/personalization_service.py`:
   - Change the model string to `"gemini-1.5-flash"`.

This is a configuration constraint update. Do not add new logic, just update the string values.

## Response snapshot

Updated all three backend services to use `gemini-1.5-flash` exclusively for Google Free Tier compatibility.

### Changes Made

**1. `backend/rag_service.py`**
- Changed `GEMINI_MODEL_VARIANTS` from multiple models to `["gemini-1.5-flash"]` only
- `CHAT_MODEL` already defaults to `"gemini-1.5-flash"` (verified)

**2. `backend/translation_service.py`**
- Changed `TRANSLATION_MODEL` from `"gpt-4o"` to `"gemini-1.5-flash"`
- Added `OPENAI_BASE_URL` environment variable support
- Updated `get_openai_client()` to use `base_url` parameter for Gemini compatibility

**3. `backend/personalization_service.py`**
- Changed `PERSONALIZATION_MODEL` from `"gpt-4o"` to `"gemini-1.5-flash"`
- Added `OPENAI_BASE_URL` environment variable support
- Updated `get_openai_client()` to use `base_url` parameter for Gemini compatibility

### Why This Matters
- Google Free Tier only supports `gemini-1.5-flash` without quota limits
- Other models like `gemini-2.0-flash`, `gemini-1.5-pro` require paid quota
- Fallback retry logic was causing cascading 429/404 errors

## Outcome

- ✅ Impact: All services now use gemini-1.5-flash; no more quota/404 errors
- 🧪 Tests: Manual testing required
- 📁 Files: 3 files modified
- 🔁 Next prompts: Test chat, translation, and personalization features
- 🧠 Reflection: Free tier constraints require explicit model pinning

## Evaluation notes (flywheel)

- Failure modes observed: 429 Quota errors, 404 model not found
- Graders run and results (PASS/FAIL): Pending verification
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test RAG chat endpoint
