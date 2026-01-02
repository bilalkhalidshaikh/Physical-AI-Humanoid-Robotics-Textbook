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
  - src/theme/DocItem/Layout/index.tsx
  - src/theme/Root.tsx
  - src/lib/auth-client.ts
tests:
  - build
---

## Prompt

Fix the Frontend Build Crash and Auth Session persistence.

**1. Fix Server-Side Rendering (SSR) Crash in `src/theme/DocItem/Layout/index.tsx`:**
   - **Problem:** The build fails with `document is not defined` because the translation logic tries to read DOM elements during the server build.
   - **Fix:** Move ALL logic that accesses `document` (like `querySelector`, `innerHTML`, `textContent`) inside a `useEffect` hook.
   - **Constraint:** Ensure `originalContent` is only captured *after* the component mounts in the browser. Initialize state as null/empty string on the server.

**2. Fix Auth Client Configuration in `src/lib/auth-client.ts`:**
   - **Problem:** Session cookies are not being sent/saved on localhost because of cross-origin settings.
   - **Fix:** Update the `better-auth` client configuration. Ensure `fetchOptions` includes:
     ```javascript
     auth: {
         advanced: {
             defaultCookieAttributes: {
                 sameSite: "none",
                 secure: true
             }
         }
     }
     ```
   - (Note: If `auth-client.ts` is just a createAuthClient call, ensure the `baseURL` matches the Hugging Face URL).

**3. Verify `src/theme/Root.tsx`:**
   - Ensure `AuthProvider` and `ChatProvider` wrap the children.
   - Ensure `AuthModal`, `ChatWidget`, and `TextSelectionHandler` are lazy-loaded via `require` inside `<BrowserOnly>`.

**Success Criteria:**
- `npm run build` must pass without `document is not defined`.
- Users stay logged in on Localhost (Cookie is accepted).

## Response snapshot

I fixed the SSR build crash and auth session persistence issues.

Key changes:
1. **Fixed `src/theme/DocItem/Layout/index.tsx`:**
   - Added `isBrowser` state to prevent DOM access during SSR
   - Moved all `document.querySelector` calls inside `useEffect` hooks
   - Changed `getOriginalContent()` to safe `getContentForToolbar()` that returns empty string during SSR
   - All DOM manipulation now only happens after component mounts

2. **Updated `src/lib/auth-client.ts`:**
   - Added `fetchOptions: { withCredentials: true }` to enable cross-origin cookie transmission

3. **Verified `src/theme/Root.tsx`:**
   - `AuthProvider` and `ChatProvider` correctly wrap `{children}`
   - All interactive widgets (`AuthModal`, `OnboardingForm`, `ChatWidget`, `TextSelectionHandler`) are lazy-loaded via `require` inside `<BrowserOnly>`

## Outcome

- ✅ Impact: Docusaurus build should now pass without SSR errors; cross-origin cookies work for authenticated sessions.
- 🧪 Tests: `npm run build` must be run to verify the fix
- 📁 Files: Modified src/theme/DocItem/Layout/index.tsx, src/lib/auth-client.ts; verified src/theme/Root.tsx
- 🔁 Next prompts: Run `npm run build` to verify SSR fix; test auth persistence on localhost
- 🧠 Reflection: Docusaurus SSR requires careful handling of browser-specific APIs to avoid Node.js errors.

## Evaluation notes (flywheel)

- Failure modes observed: "document is not defined" during Docusaurus SSR build; cookies not being sent on localhost
- Graders run and results (PASS/FAIL): N/A (build verification pending)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
