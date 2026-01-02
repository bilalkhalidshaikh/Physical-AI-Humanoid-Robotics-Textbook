---
id: 018
title: Fix Cross-Origin Session Cookies
stage: green
date: 2026-01-01
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: 002-chatbot-auth
user: Bilal Khalid
command: /sp.implement
labels: ["auth", "cookies", "cors", "better-auth"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - auth-server/src/auth.ts
tests:
  - null
---

## Prompt

Update the Auth Server configuration to fix Cross-Origin Session Cookies.

Problem:
The Auth Server (on Hugging Face) sends a session cookie, but the Browser (on Localhost) blocks it because of security policies.

Required Changes in `auth-server/src`:
1.  Find the `better-auth` configuration (likely `src/auth.ts` or `src/index.ts`).
2.  Update the `advanced` settings to strictly enforce:
    - `defaultCookieAttributes`:
      - `sameSite: "none"`
      - `secure: true`
      - `partitioned: true`
3.  Update `trustedOrigins` to include:
    - "http://localhost:3000"
    - "https://bilalkhalidshaikh.github.io"

Goal:
The server must send cookies marked as "SameSite=None; Secure" so the browser accepts them.

## Response snapshot

I have updated the BetterAuth configuration in `auth-server/src/auth.ts` to strictly enforce cross-origin session cookies and expand the trusted origins.

Key changes:
- Added `defaultCookieAttributes` to `advanced` settings with `sameSite: "none"`, `secure: true`, and `partitioned: true`.
- Updated `trustedOrigins` to explicitly include `http://localhost:3000` and `https://bilalkhalidshaikh.github.io`.

## Outcome

- ✅ Impact: Auth server now sends cross-origin compatible cookies (SameSite=None; Secure).
- 🧪 Tests: N/A
- 📁 Files: Modified `auth-server/src/auth.ts`.
- 🔁 Next prompts: Verify authentication flow between Hugging Face auth server and Localhost/GitHub Pages frontend.
- 🧠 Reflection: For BetterAuth to work across different domains, specific cookie attributes are required by modern browsers.

## Evaluation notes (flywheel)

- Failure modes observed: Browser blocking session cookies due to missing SameSite=None and Secure attributes.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
