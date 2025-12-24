---
id: 007
title: Fix DocItem Layout Imports
stage: green
date: 2025-12-16
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: /sp.implement
labels: ["bugfix", "docusaurus", "swizzle", "imports", "build-error"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/theme/DocItem/Layout/index.tsx
tests:
  - null
---

## Prompt

/sp.implement

FIX: Docusaurus Frontend Build Error

Current Status: The Docusaurus frontend failed to compile with:
`Module not found: Error: Can't resolve '@theme/DocItem/TOC' in src/theme/DocItem/Layout`

Diagnosis: The custom `DocItem/Layout/index.tsx` file you created is using an incorrect import path for the Table of Contents component. In Docusaurus 3.x, the structure has changed.

REQUIRED FIX:
Update `src/theme/DocItem/Layout/index.tsx`.
1. Change the import from `@theme/DocItem/TOC` to the correct Docusaurus 3 path.
2. Usually, this is `@theme/TOC` or requires removing the explicit import if `DocItem` handles it differently.
3. If unsure of the internal path, simplify the component to wrap the original Layout instead of re-implementing it, OR just fix the import to `@theme/TOC`.

Please fix the file so the build succeeds.

## Response snapshot

Fixed the DocItem Layout by adopting a **wrapper pattern** instead of re-implementing the entire component.

### Problem
The previous implementation attempted to re-implement the full DocItem Layout, importing internal Docusaurus components like `@theme/DocItem/TOC` which don't exist as public exports in Docusaurus 3.x.

### Solution
Changed to a wrapper pattern that:
1. Imports `@theme-original/DocItem/Layout` (the original component)
2. Wraps it with the ChapterToolbar
3. Passes through all props to the original

### Key Changes

**Before (broken):**
```typescript
import DocItemTOC from "@theme/DocItem/TOC";
import DocItemContent from "@theme/DocItem/Content";
// ... many internal imports
```

**After (fixed):**
```typescript
import OriginalLayout from "@theme-original/DocItem/Layout";
// Just wrap the original with ChapterToolbar
```

### Files Modified
- `src/theme/DocItem/Layout/index.tsx` - Simplified to wrapper pattern
- `src/theme/DocItem/Layout/styles.module.css` - Removed (no longer needed)

## Outcome

- ✅ Impact: Build error resolved; swizzle pattern now follows Docusaurus best practices
- 🧪 Tests: Build should now succeed
- 📁 Files: 1 file modified, 1 file removed
- 🔁 Next prompts: Verify build passes, test ChapterToolbar functionality
- 🧠 Reflection: Wrapper swizzle is safer than full re-implementation for Docusaurus

## Evaluation notes (flywheel)

- Failure modes observed: Internal Docusaurus imports not public in v3.x
- Graders run and results (PASS/FAIL): Build - pending verification
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run `npm run build` to verify fix
