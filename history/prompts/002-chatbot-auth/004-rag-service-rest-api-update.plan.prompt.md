---
id: 004
title: RAG Service REST API Update
stage: plan
date: 2025-12-16
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: /sp.plan
labels: ["rag", "qdrant", "rest-api", "windows-fix", "gemini"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-chatbot-auth/plan.md
  - backend/rag_service.py
  - backend/.env.example
tests:
  - null
---

## Prompt

Update the Technical Plan for the RAG Service (Phase 4).
Current Issue: The `qdrant-client` library on Windows is throwing `AttributeError: 'QdrantClient' object has no attribute 'search'`, indicating a corrupted or incompatible gRPC installation.
Required Change: Modify the implementation plan for `backend/rag_service.py` to use a "Robust Implementation Strategy."
1. Instead of relying on the standard `QdrantClient` class (which is failing), the implementation must use a custom `RobustQdrantClient` class.
2. This class should implement the `.search()` method manually using `httpx` to send raw REST API requests to the Qdrant Cloud endpoint (`/collections/{name}/points/search`).
3. This bypasses the local gRPC dependency issues completely.
4. Ensure `OPENAI_BASE_URL` is correctly configured for Google Gemini compatibility.
This is a critical fix to ensure the chatbot works on the deployment environment.

## Response snapshot

Updated the technical plan (`specs/002-chatbot-auth/plan.md`) with:
1. New "RAG Service - Robust Implementation Strategy" section in Phase 4
2. Added Windows gRPC issue to Risk Mitigation table
3. Added httpx REST API decision to Architecture Decisions table

Implemented `RobustQdrantClient` class in `backend/rag_service.py`:
- Custom client using httpx for REST API calls to Qdrant Cloud
- Both sync (`search`) and async (`search_async`) methods
- `QdrantSearchHit` wrapper class for result compatibility
- Support for `OPENAI_BASE_URL` environment variable for Gemini compatibility
- Support for `CHAT_MODEL` environment variable

Updated `backend/.env.example` with:
- Gemini configuration documentation
- REST API endpoint notation for Qdrant (port 6333)

## Outcome

- ✅ Impact: Critical fix for Windows deployment - RAG service now bypasses gRPC entirely
- 🧪 Tests: Manual testing required - no automated tests added
- 📁 Files: 3 files modified (plan.md, rag_service.py, .env.example)
- 🔁 Next prompts: Test RAG chatbot with Gemini API, verify Qdrant REST API connectivity
- 🧠 Reflection: REST API approach is more portable and debuggable than gRPC

## Evaluation notes (flywheel)

- Failure modes observed: qdrant-client gRPC incompatibility on Windows
- Graders run and results (PASS/FAIL): N/A - manual verification needed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test with live Qdrant Cloud endpoint
