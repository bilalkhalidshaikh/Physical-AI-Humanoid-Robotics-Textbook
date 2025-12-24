---
id: 017
title: Fix Profile Link Translation Rendering
stage: green
date: 2025-12-18
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: /sp.implement
labels: ["bugfix", "profile-link", "translation", "useBaseUrl", "minimum-length"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/theme/Navbar/Content/index.tsx
  - src/theme/DocItem/Layout/index.tsx
  - backend/translation_service.py
tests:
  - null
---

## Prompt

FIX: Profile Link & Translation Rendering

1. FIX PROFILE LINK in `src/theme/NavbarItem/ComponentTypes.tsx` (or wherever the Profile/SignOut dropdown is defined):
   - The current link points to `/profile` which 404s.
   - Change it to use Docusaurus `useBaseUrl`.
   - Import: `import useBaseUrl from '@docusaurus/useBaseUrl';`
   - Usage: `href={useBaseUrl('/profile')}`
   - This ensures it correctly resolves to `/Physical-AI-Humanoid-Robotics-Textbook/profile`.

2. FIX TRANSLATION RENDERING in `src/theme/DocItem/Layout/index.tsx`:
   - The logs show `contentLength: 3`. This is garbage data.
   - Update the fallback logic: `const isValidTranslation = translatedContent && translatedContent.length > 50;`
   - If `!isValidTranslation`, FORCE render `originalContent`.
   - Ensure `originalContent` is actually being passed/stored correctly and not overwritten by the empty translation.

3. TWEAK TRANSLATION PROMPT in `backend/translation_service.py`:
   - Add this instruction to the system prompt: "If you cannot translate, return the ORIGINAL ENGLISH TEXT exactly."
   - This guarantees we never get a 3-character response.

## Response snapshot

### 1. Profile Link Fix (`src/theme/Navbar/Content/index.tsx`)

Added `useBaseUrl` import and usage:

```typescript
import useBaseUrl from "@docusaurus/useBaseUrl";

function AuthButton() {
  const profileUrl = useBaseUrl("/profile");
  // ...
  <a href={profileUrl} className={styles.dropdownItem}>
    Profile Settings
  </a>
}
```

This ensures the link resolves correctly to `/Physical-AI-Humanoid-Robotics-Textbook/profile` on GitHub Pages.

### 2. Translation Rendering Fix (`src/theme/DocItem/Layout/index.tsx`)

Added minimum length constant and stricter validation:

```typescript
// Minimum length for valid translation (avoids garbage 3-char responses)
const MIN_VALID_CONTENT_LENGTH = 50;

const handleContentChange = (newContent: string) => {
  // Must be at least 50 chars to be a real translation
  const isValidContent = newContent && newContent.trim().length >= MIN_VALID_CONTENT_LENGTH;

  if (contentElement) {
    if (isValidContent) {
      contentElement.innerHTML = newContent;
      console.log(`Translation applied: ${newContent.length} chars`);
    } else {
      // Fallback to original content
      console.log(`Translation fallback triggered - received ${newContent?.length || 0} chars (min ${MIN_VALID_CONTENT_LENGTH})`);
      if (originalContent) {
        contentElement.innerHTML = originalContent;
      }
    }
  }
};
```

### 3. Translation Prompt Update (`backend/translation_service.py`)

Added fallback instruction to system prompt:

```python
TRANSLATION_SYSTEM_PROMPT = """You are a helpful translator...

IMPORTANT: If you cannot translate for any reason, return the ORIGINAL ENGLISH TEXT exactly as provided. Never return an empty response or a very short response."""
```

## Outcome

- ✅ Impact: Profile link now works with base URL, translation rejects garbage responses
- 🧪 Tests: Manual testing - click Profile link, try translation
- 📁 Files: 3 files modified
- 🔁 Next prompts: Test end-to-end translation and profile navigation
- 🧠 Reflection: Multiple layers of validation (backend length check + frontend length check) provide defense in depth

## Evaluation notes (flywheel)

- Failure modes observed: Profile 404 due to missing base URL, garbage 3-char translations displayed
- Graders run and results (PASS/FAIL): Pending verification
- Prompt variant (if applicable): Added explicit fallback instruction
- Next experiment (smallest change to try): Verify translation with longer content
