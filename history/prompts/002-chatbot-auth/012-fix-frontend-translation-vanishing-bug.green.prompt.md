---
id: 012
title: Fix Frontend Translation Vanishing Bug
stage: green
date: 2025-12-17
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: manual
labels: ["bugfix", "frontend", "translation", "personalization", "defensive-programming"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/components/ChapterToolbar/index.tsx
  - src/theme/DocItem/Layout/index.tsx
tests:
  - null
---

## Prompt

FIX: Frontend Translation Vanishing Bug

The "Translate to Urdu" feature causes the page content to disappear if the backend returns an error or empty response.

REQUIRED CHANGE:
Update `src/theme/DocItem/Layout/index.tsx`:
- In the translation logic, ensure `docContent` is NEVER set to null or empty string.
- If the API call fails, keep showing the original English content.
- Add a `try/catch` block around the translation API call in the frontend component.
- If an error occurs, `setTranslatedContent(originalContent)` (or equivalent) so the user still sees text.

Do not let the component render nothing. Always render original content as fallback.

## Response snapshot

Fixed the frontend translation vanishing bug with a two-layer defensive approach:

### Layer 1: ChapterToolbar Component (`src/components/ChapterToolbar/index.tsx`)

**handleTranslate function** (lines 44-52):
```typescript
// Validate response - never set empty content (prevents vanishing bug)
const translatedContent = response?.translated_content;
if (translatedContent && translatedContent.trim().length > 0) {
  onContentChange(translatedContent);
  setViewMode("translated");
} else {
  // API returned empty/null - keep original content visible
  setError("Translation returned empty content. Showing original.");
}
```

**handlePersonalize function** (lines 88-96):
```typescript
// Validate response - never set empty content (prevents vanishing bug)
const personalizedContent = response?.personalized_content;
if (personalizedContent && personalizedContent.trim().length > 0) {
  onContentChange(personalizedContent);
  setViewMode("personalized");
} else {
  // API returned empty/null - keep original content visible
  setError("Personalization returned empty content. Showing original.");
}
```

### Layer 2: DocItem Layout Component (`src/theme/DocItem/Layout/index.tsx`)

**handleContentChange function** (lines 39-44):
```typescript
// Safety: Never set empty content to prevent vanishing bug
const handleContentChange = (newContent: string) => {
  if (contentElement && newContent && newContent.trim().length > 0) {
    contentElement.innerHTML = newContent;
    setDisplayContent(newContent);
  }
  // If newContent is empty/null, silently ignore to prevent vanishing
};
```

### Key Improvements

1. **Response validation**: Check `response?.translated_content` before using
2. **Empty string check**: Verify `trim().length > 0` to catch whitespace-only responses
3. **User feedback**: Show error message when API returns empty content
4. **Silent ignore**: Layout layer silently rejects empty content as last defense
5. **Original preserved**: Never call `onContentChange()` on error - original stays visible

## Outcome

- ✅ Impact: Translation/personalization failures no longer cause content to vanish
- 🧪 Tests: Manual testing required - trigger translation with backend offline
- 📁 Files: 2 files modified
- 🔁 Next prompts: Test translation toggle, verify error messages display correctly
- 🧠 Reflection: Defense in depth - validate at both API consumer and DOM manipulator layers

## Evaluation notes (flywheel)

- Failure modes observed: Content vanishing when API returns null/empty/error
- Graders run and results (PASS/FAIL): Pending verification
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test with backend returning 500 error
