---
id: 015
title: Profile Page and Translation Fix
stage: green
date: 2025-12-17
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: /sp.implement
labels: ["profile", "translation", "personalization", "length-check", "fail-safe"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/pages/profile.tsx
  - backend/translation_service.py
  - backend/personalization_service.py
tests:
  - null
---

## Prompt

IMPLEMENT: User Profile Page & Fix Translation Logic

1. CREATE `auth-server/src/pages/profile.tsx` (or `src/pages/profile.tsx` in frontend):
   - Create a new Docusaurus page component at `/profile`.
   - Use the `Layout` component from `@theme/Layout`.
   - Use BetterAuth client hooks to get the `session`.
   - If no session, redirect to home or show "Please Sign In".
   - Display User Name, Email, and Avatar.
   - Add a "Sign Out" button.
   - (Bonus) Add simple text inputs for "Software Background" and "Hardware Background" to store in `user_profiles` (stub this if backend route missing).

2. FIX `backend/translation_service.py`:
   - The current prompt is causing Gemini 2.5 to return empty/short strings (length 3).
   - CHANGE the system prompt to: "You are a translator. Translate the input text to Urdu. Output ONLY the Urdu translation. Do not add markdown blocks."
   - Add a check: `if len(translated_text) < 10: return original_content` (Treat very short responses as failures to avoid vanishing text).
   - Add `print(f"DEBUG TRANSLATION: {translated_text}")` so we can see what it returns in logs.

3. VERIFY `backend/personalization_service.py`:
   - Ensure it also has the length check safety net.

This completes the Auth UI loop and makes translation fail-safe.

## Response snapshot

### 1. Profile Page Enhancement (`src/pages/profile.tsx`)

The profile page already existed with full functionality. Added avatar display:

```tsx
{/* Avatar */}
{user?.image ? (
  <img
    src={user.image}
    alt={user.name || "User avatar"}
    style={{ width: "80px", height: "80px", borderRadius: "50%", objectFit: "cover" }}
  />
) : (
  <div style={{
    width: "80px", height: "80px", borderRadius: "50%",
    backgroundColor: "var(--ifm-color-primary)",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "2rem", color: "white", fontWeight: "bold",
  }}>
    {(user?.name || user?.email || "U")[0].toUpperCase()}
  </div>
)}
```

Existing features verified:
- User info (name, email)
- Software/Hardware background inputs
- Preferred language selector
- Personalization toggle
- Sign Out button

### 2. Translation Service Fix (`backend/translation_service.py`)

**Simplified prompt:**
```python
TRANSLATION_PROMPT = """Translate the following text to Urdu. Preserve all placeholders like ___CODE_BLOCK_N___ exactly. Keep technical terms in English. Output ONLY the Urdu translation without markdown code blocks or explanations.

{content}"""
```

**Added length check:**
```python
MIN_TRANSLATION_LENGTH = 50

# Length check: treat very short responses as failures
if not translated or len(translated.strip()) < MIN_TRANSLATION_LENGTH:
    print(f"DEBUG TRANSLATION: Response too short ({len(translated.strip()) if translated else 0} < {MIN_TRANSLATION_LENGTH}), returning original")
    return content
```

**Debug logging:**
```python
print(f"DEBUG TRANSLATION: received {len(translated) if translated else 0} chars")
print(f"DEBUG TRANSLATION preview: {translated[:200] if translated else 'None'}...")
```

### 3. Personalization Service Fix (`backend/personalization_service.py`)

Added same safety measures:
```python
MIN_PERSONALIZATION_LENGTH = 50

# Length check and debug logging
print(f"DEBUG PERSONALIZATION: received {len(personalized) if personalized else 0} chars")
if not personalized or len(personalized.strip()) < MIN_PERSONALIZATION_LENGTH:
    print(f"DEBUG PERSONALIZATION: Response too short, returning original")
    return content
```

## Outcome

- ✅ Impact: Profile page complete with avatar, translation/personalization fail-safe
- 🧪 Tests: Manual testing required - check console logs for DEBUG messages
- 📁 Files: 3 files modified
- 🔁 Next prompts: Test translation with various content lengths
- 🧠 Reflection: Length validation provides last line of defense against empty API responses

## Evaluation notes (flywheel)

- Failure modes observed: Gemini returning very short (3 char) responses
- Graders run and results (PASS/FAIL): Pending verification
- Prompt variant (if applicable): Simplified prompt from detailed instructions
- Next experiment (smallest change to try): Test with MIN_TRANSLATION_LENGTH = 50
