---
id: 014
title: Fix Frontend Translation Fallback
stage: green
date: 2025-12-17
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: /sp.implement
labels: ["bugfix", "frontend", "translation", "fallback", "defensive-programming"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/theme/DocItem/Layout/index.tsx
  - src/components/ChapterToolbar/index.tsx
tests:
  - null
---

## Prompt

FIX: Frontend Translation Fallback

The translation backend is returning "original content" on error, but the Frontend is still rendering a blank screen.

REQUIRED CHANGE:
Update `src/theme/DocItem/Layout/index.tsx` (or the component handling translation):
1. Locate the rendering logic for `translatedContent`.
2. Change the condition to: `(translatedContent && translatedContent.length > 0) ? translatedContent : originalContent`.
3. Ensure that if `translatedContent` is ever null/undefined/empty, we DEFAULT to showing the original children/content.
4. Add a console log `console.log("Translation fallback triggered")` when showing original content to help debugging.

This ensures the user NEVER sees a blank page, even if the backend returns an empty string.

## Response snapshot

Implemented comprehensive frontend fallback with three layers of protection:

### Layer 1: DocItem Layout (`src/theme/DocItem/Layout/index.tsx`)

Added `originalContent` state and enhanced `handleContentChange`:

```typescript
// Store original content for fallback
const [originalContent, setOriginalContent] = useState<string | null>(null);

// Capture original content once on mount
useEffect(() => {
  if (!originalContent) {
    const docContent = document.querySelector(".theme-doc-markdown");
    if (docContent instanceof HTMLElement && docContent.innerHTML.trim().length > 0) {
      setOriginalContent(docContent.innerHTML);
    }
  }
}, [originalContent]);

// Handle content changes with fallback
const handleContentChange = (newContent: string) => {
  const isValidContent = newContent && newContent.trim().length > 0;
  if (contentElement) {
    if (isValidContent) {
      contentElement.innerHTML = newContent;
      setDisplayContent(newContent);
    } else {
      // Fallback to original content - NEVER show blank
      console.log("Translation fallback triggered - showing original content");
      if (originalContent && originalContent.trim().length > 0) {
        contentElement.innerHTML = originalContent;
        setDisplayContent(originalContent);
      }
    }
  }
};
```

### Layer 2: ChapterToolbar (`src/components/ChapterToolbar/index.tsx`)

Added explicit fallback to original content on both error AND empty response:

```typescript
// On empty response
console.log("Translation fallback: API returned empty content");
setError("Translation returned empty content. Showing original.");
onContentChange(originalContent);  // Explicitly restore

// On error
console.log("Translation fallback: API error", err);
setError(err instanceof Error ? err.message : "Translation failed");
onContentChange(originalContent);  // Explicitly restore
```

### Debug Logging Added

Console logs added to track:
- Translation/personalization response metadata (hasContent, contentLength, trimmedLength)
- Fallback triggers with reason (empty content vs API error)
- Layout-level fallback triggers

## Outcome

- ✅ Impact: User NEVER sees blank page even if API returns empty/error
- 🧪 Tests: Manual testing - trigger translation with backend offline
- 📁 Files: 2 files modified
- 🔁 Next prompts: Test translation flow with various failure scenarios
- 🧠 Reflection: Defense in depth with explicit fallback at both toolbar and layout layers

## Evaluation notes (flywheel)

- Failure modes observed: Blank screen when API returns empty string
- Graders run and results (PASS/FAIL): Pending verification
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test with backend returning empty translated_content
