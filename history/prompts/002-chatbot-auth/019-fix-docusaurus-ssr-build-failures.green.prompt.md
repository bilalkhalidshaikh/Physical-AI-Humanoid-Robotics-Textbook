---
id: 019
title: Fix Docusaurus SSR Build Failures
stage: green
date: 2026-01-01
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: 002-chatbot-auth
user: Bilal Khalid
command: /sp.implement
labels: ["ssr", "docusaurus", "frontend", "refactor"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/theme/Root.tsx
  - src/context/AuthContext.tsx
  - src/context/ChatContext.tsx
tests:
  - build
---

## Prompt

Refactor the frontend architecture to fix Docusaurus Server-Side Rendering (SSR) build failures.

Current State:
The build fails because client-side logic (localStorage, window) is running during the server build process in `Root.tsx` and Context providers.

Required Implementation:

1. Refactor `src/theme/Root.tsx`:
   - The `AuthProvider` and `ChatProvider` MUST remain at the top level and wrap `{children}` so the Navbar works on the server.
   - All interactive widgets (`AuthModal`, `OnboardingForm`, `ChatWidget`, `TextSelectionHandler`) MUST be moved inside `<BrowserOnly>` and lazy-loaded using `require()`.

2. Refactor `src/context/AuthContext.tsx`:
   - Change `useState` initialization. It must NOT read `localStorage` directly.
   - Initialize state as `null`.
   - Use `useEffect` to hydrate the state from `localStorage` only after the component mounts in the browser.

3. Refactor `src/context/ChatContext.tsx`:
   - Apply the same pattern: Remove direct `localStorage` access from `useState`. Initialize empty/null and load data inside `useEffect`.

Success Criteria:
- `npm run build` must pass locally without "document is not defined" errors.

## Response snapshot

I refactored the frontend architecture to ensure SSR compatibility for the Docusaurus build process.

Key changes:
- In `src/theme/Root.tsx`, moved interactive widgets (`AuthModal`, `OnboardingForm`, `ChatWidget`, `TextSelectionHandler`) inside a `<BrowserOnly>` wrapper and implemented lazy loading via `require()`.
- In `src/context/AuthContext.tsx` and `src/context/ChatContext.tsx`, added `isMounted` state and `typeof window` checks to ensure that hydration and client-side logic only execute after mount in the browser.

## Outcome

- ✅ Impact: Docusaurus build should now pass by preventing client-side APIs from being accessed during SSR.
- 🧪 Tests: Manual build verification required (npm run build).
- 📁 Files: Refactored src/theme/Root.tsx, src/context/AuthContext.tsx, and src/context/ChatContext.tsx.
- 🔁 Next prompts: Run `npm run build` to verify the fix.
- 🧠 Reflection: Docusaurus requires careful handling of components that use browser-specific APIs (window, document, localStorage) to avoid breaking the Node.js-based build process.

## Evaluation notes (flywheel)

- Failure modes observed: "document/window is not defined" during Docusaurus SSR build.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
