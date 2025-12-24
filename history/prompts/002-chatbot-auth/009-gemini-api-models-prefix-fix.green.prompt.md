---
id: 009
title: Gemini API Models Prefix Fix
stage: green
date: 2025-12-16
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: /sp.implement
labels: ["config", "gemini", "api", "models-prefix", "404-fix"]
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

FIX: Gemini API Configuration

The backend is crashing with 404 errors because the Google API requires the `models/` prefix for model names, but the client configuration is stripping it or the base URL includes `openai/`.

REQUIRED CHANGES:

1. Update `backend/.env.example`:
   - Change `OPENAI_BASE_URL` to `https://generativelanguage.googleapis.com/v1beta/` (remove `openai/`).

2. Update `backend/rag_service.py`, `backend/translation_service.py`, and `backend/personalization_service.py`:
   - Update `get_openai_client` to use the correct base_url.
   - Hardcode the model constants to include the prefix:
     - `CHAT_MODEL = "models/gemini-1.5-flash"`
     - `TRANSLATION_MODEL = "models/gemini-1.5-flash"`
     - `PERSONALIZATION_MODEL = "models/gemini-1.5-flash"`
   - Update `GEMINI_MODEL_VARIANTS` in `rag_service.py` to use the `models/` prefix for all entries.

This ensures compatibility with the Google API endpoint.

## Response snapshot

Updated all backend services to use `models/` prefix for Google Gemini API compatibility.

### Changes Made

**1. `backend/.env.example`**
- Changed `OPENAI_BASE_URL` from `https://generativelanguage.googleapis.com/v1beta/openai/` to `https://generativelanguage.googleapis.com/v1beta/`
- Updated documentation to show `models/` prefix requirement

**2. `backend/rag_service.py`**
- Changed `CHAT_MODEL` default to `"models/gemini-1.5-flash"`
- Changed `GEMINI_MODEL_VARIANTS` to `["models/gemini-1.5-flash"]`
- Changed `EMBEDDING_MODEL` to `"models/text-embedding-004"`

**3. `backend/translation_service.py`**
- Changed `TRANSLATION_MODEL` to `"models/gemini-1.5-flash"`

**4. `backend/personalization_service.py`**
- Changed `PERSONALIZATION_MODEL` to `"models/gemini-1.5-flash"`

### Technical Context

The Google Generative AI API requires model names to include the `models/` prefix (e.g., `models/gemini-1.5-flash`). When using the OpenAI-compatible endpoint without this prefix, the API returns 404 errors because it cannot resolve the model path.

## Outcome

- ✅ Impact: All services now use correct model path format for Google API
- 🧪 Tests: Manual testing required
- 📁 Files: 4 files modified
- 🔁 Next prompts: Restart backend and test chat/translation/personalization
- 🧠 Reflection: Google API path requirements differ from OpenAI compatibility layer docs

## Evaluation notes (flywheel)

- Failure modes observed: 404 model not found due to missing models/ prefix
- Graders run and results (PASS/FAIL): Pending verification
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test RAG chat with new config
