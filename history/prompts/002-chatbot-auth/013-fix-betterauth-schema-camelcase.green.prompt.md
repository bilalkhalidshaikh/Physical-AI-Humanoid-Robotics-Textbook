---
id: 013
title: Fix BetterAuth Schema CamelCase
stage: green
date: 2025-12-17
surface: agent
model: claude-sonnet-4.5
feature: 002-chatbot-auth
branch: main
user: Bilal Khalid
command: /sp.implement
labels: ["bugfix", "auth", "betterauth", "schema", "drizzle", "camelCase"]
links:
  spec: specs/002-chatbot-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - auth-server/src/db/schema.ts
tests:
  - null
---

## Prompt

FIX: Propagate Gemini 2.5 Flash & Fix Translation Bug

The user has confirmed `gemini-2.5-flash` is the working model. The current `translation_service.py` is likely using an old model or failing, causing the frontend to render empty content.

REQUIRED IMPLEMENTATION:

1. Update `backend/translation_service.py`:
   - Set `TRANSLATION_MODEL = "gemini-2.5-flash"`.
   - Ensure `OPENAI_BASE_URL` loads from env and is passed to the client.
   - CRITICAL: Add a `try/except` block. If the API call fails or returns empty, RETURN THE ORIGINAL `content`. Do not return None or raise an error. This prevents the UI from vanishing.

2. Update `backend/personalization_service.py`:
   - Set `PERSONALIZATION_MODEL = "gemini-2.5-flash"`.
   - Add the same `try/except` fallback to return original content on failure.

3. Update `backend/.env.example`:
   - Update `CHAT_MODEL` to `gemini-2.5-flash`.

4. Update `auth-server/src/db/schema.ts`:
   - Fix the BetterAuth schema mismatch.
   - Change `provider_account_id` to `accountId`.
   - Change `user_id` to `userId`.
   - Change `session_token` (or token) to `sessionToken`.
   - Ensure table definitions match BetterAuth's default expectations exactly (camelCase fields).

Do not modify `rag_service.py` as it is already working.

## Response snapshot

### Verification: Backend Services Already Configured

Verified that all backend services already have the correct configuration:

| File | Constant | Value | Error Handling |
|------|----------|-------|----------------|
| `translation_service.py` | `TRANSLATION_MODEL` | `"gemini-2.5-flash"` | Returns original on failure |
| `personalization_service.py` | `PERSONALIZATION_MODEL` | `"gemini-2.5-flash"` | Returns original on failure |
| `backend/.env.example` | `CHAT_MODEL` | `"gemini-2.5-flash"` | N/A |

### BetterAuth Schema Fix (`auth-server/src/db/schema.ts`)

Fixed all BetterAuth tables to use camelCase column names (BetterAuth's default expectation):

**Users Table:**
```typescript
emailVerified: boolean("emailVerified").default(false),
createdAt: timestamp("createdAt", { withTimezone: true }),
updatedAt: timestamp("updatedAt", { withTimezone: true }),
```

**Sessions Table:**
```typescript
userId: text("userId").notNull(),  // Was "user_id"
expiresAt: timestamp("expiresAt", { withTimezone: true }),  // Was "expires_at"
ipAddress: text("ipAddress"),  // Was "ip_address"
userAgent: text("userAgent"),  // Was "user_agent"
createdAt: timestamp("createdAt", { withTimezone: true }),
updatedAt: timestamp("updatedAt", { withTimezone: true }), // Added
```

**Accounts Table:**
```typescript
userId: text("userId").notNull(),  // Was "user_id"
providerId: text("providerId").notNull(),  // Was "provider"
accountId: text("accountId").notNull(),  // Was "provider_account_id"
accessToken: text("accessToken"),  // Was "access_token"
refreshToken: text("refreshToken"),  // Was "refresh_token"
accessTokenExpiresAt: timestamp("accessTokenExpiresAt"),  // Was "expires_at"
refreshTokenExpiresAt: timestamp("refreshTokenExpiresAt"),  // Added
idToken: text("idToken"),  // Added
password: text("password"),  // Added for email/password auth
createdAt: timestamp("createdAt", { withTimezone: true }),
updatedAt: timestamp("updatedAt", { withTimezone: true }),  // Added
```

**Verification Table:**
```typescript
expiresAt: timestamp("expiresAt", { withTimezone: true }),  // Was "expires_at"
createdAt: timestamp("createdAt", { withTimezone: true }),
updatedAt: timestamp("updatedAt", { withTimezone: true }),
```

### Key Insight

BetterAuth expects camelCase column names by default. The original schema used snake_case for database columns (e.g., `user_id`, `provider_account_id`), causing BetterAuth to fail when looking up fields.

## Outcome

- ✅ Impact: BetterAuth schema now matches expected column names
- 🧪 Tests: Manual testing required - run database migration and test auth flow
- 📁 Files: 1 file modified (auth-server/src/db/schema.ts)
- 🔁 Next prompts: Run drizzle-kit push to apply schema changes, test GitHub OAuth
- 🧠 Reflection: BetterAuth's Drizzle adapter expects camelCase column names matching JS property names

## Evaluation notes (flywheel)

- Failure modes observed: BetterAuth failing to find expected columns due to snake_case naming
- Graders run and results (PASS/FAIL): Pending migration
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Push schema and test login flow
