---
id: 011
title: Propagate Gemini 2.5 Flash Configuration
stage: green
date: 2025-12-17
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: manual
labels: ["config", "gemini", "model-fix", "error-handling", "graceful-degradation"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/translation_service.py
  - backend/personalization_service.py
  - backend/.env.example
tests:
  - null
---

## Prompt

FIX: Propagate Gemini 2.5 Flash Configuration

The user manually updated rag_service.py to use gemini-2.5-flash, which fixed the chatbot. However, translation_service.py and personalization_service.py are still using broken/old models, causing the UI to crash/vanish.

REQUIRED IMPLEMENTATION TASKS:

1. Update `backend/translation_service.py`:
   - Change `TRANSLATION_MODEL` to `"gemini-2.5-flash"`
   - Add error handling that returns original content on failure (prevent vanishing text)

2. Update `backend/personalization_service.py`:
   - Change `PERSONALIZATION_MODEL` to `"gemini-2.5-flash"`
   - Add error handling that returns original content on failure (prevent vanishing text)

3. Update `backend/.env.example`:
   - Update `CHAT_MODEL` to `gemini-2.5-flash`

## Response snapshot

Updated all backend services to use `gemini-2.5-flash` with graceful error handling.

### Configuration Applied

**`backend/.env.example`**
```
CHAT_MODEL="gemini-2.5-flash"
```

**Backend Services Updated**
| File | Model Constant | Value | Error Handling |
|------|----------------|-------|----------------|
| `translation_service.py` | `TRANSLATION_MODEL` | `"gemini-2.5-flash"` | Returns original content on failure |
| `personalization_service.py` | `PERSONALIZATION_MODEL` | `"gemini-2.5-flash"` | Returns original content on failure |

### Key Changes

1. **Translation Service** (`translation_service.py:152-156`):
   - Added try/except wrapper around entire translation logic
   - On any exception, logs warning and returns original content
   - Prevents UI vanishing when translation fails

2. **Personalization Service** (`personalization_service.py:165-169`):
   - Added try/except wrapper around personalization logic
   - On any exception, logs warning and returns original content
   - Prevents UI vanishing when personalization fails

### Graceful Degradation Pattern
```python
except Exception as e:
    # On any error, return original content to prevent vanishing text
    import logging
    logging.warning(f"[Service] failed, returning original content: {e}")
    return content
```

## Outcome

- ✅ Impact: All services now use gemini-2.5-flash with graceful error handling
- 🧪 Tests: Manual testing required - restart backend
- 📁 Files: 3 files modified
- 🔁 Next prompts: Test translation toggle, personalization features
- 🧠 Reflection: Graceful degradation prevents cascading UI failures from API errors

## Evaluation notes (flywheel)

- Failure modes observed: UI vanishing when API calls fail without error handling
- Graders run and results (PASS/FAIL): Pending verification
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test all three services with new config
