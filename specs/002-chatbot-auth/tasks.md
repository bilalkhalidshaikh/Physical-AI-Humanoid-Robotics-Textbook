# Tasks: Interactive RAG Chatbot, Authentication & Localization

**Input**: Design documents from `/specs/002-chatbot-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification. Implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure (multi-service):
- **Auth Server**: `auth-server/src/`
- **RAG Backend**: `backend/`
- **Frontend**: `src/` (Docusaurus)
- **Scripts**: `scripts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for all three services

- [x] T001 Create auth-server directory structure: `auth-server/src/`, `auth-server/src/db/`, `auth-server/src/routes/`
- [x] T002 [P] Create backend directory structure: `backend/`, `backend/db/`, `backend/models/`
- [x] T003 [P] Create scripts directory structure: `scripts/`
- [x] T004 [P] Create frontend component directories: `src/components/`, `src/theme/`, `src/context/`, `src/lib/`, `src/pages/`
- [x] T005 Initialize auth-server with package.json including hono, better-auth, @neondatabase/serverless, drizzle-orm in `auth-server/package.json`
- [x] T006 [P] Create auth-server TypeScript config in `auth-server/tsconfig.json`
- [x] T007 [P] Create backend requirements.txt with fastapi, uvicorn, openai, qdrant-client, asyncpg, python-dotenv in `backend/requirements.txt`
- [x] T008 Create environment example files: `auth-server/.env.example`, `backend/.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**Critical**: No user story work can begin until this phase is complete

### Database Schema & Migrations

- [x] T009 Create SQL migration 001_create_core_tables.sql with users, user_profiles, sessions, accounts tables in `auth-server/migrations/001_create_core_tables.sql`
- [x] T010 [P] Create SQL migration 002_create_chat_tables.sql with chat_sessions, chat_messages tables in `auth-server/migrations/002_create_chat_tables.sql`
- [x] T011 [P] Create SQL migration 003_create_cache_tables.sql with translation_cache, personalization_cache tables in `auth-server/migrations/003_create_cache_tables.sql`

### Auth Server Foundation

- [x] T012 Create Neon database connection client in `auth-server/src/db/client.ts`
- [x] T013 Create Drizzle ORM schema definitions in `auth-server/src/db/schema.ts`
- [x] T014 Configure Drizzle with drizzle.config.ts in `auth-server/drizzle.config.ts`
- [x] T015 Create BetterAuth configuration with email/password and OAuth providers in `auth-server/src/auth.ts`
- [x] T016 Create Hono app entry point with CORS and auth routes in `auth-server/src/index.ts`

### Backend Foundation

- [x] T017 Create async Postgres connection pool in `backend/db/connection.py`
- [x] T018 [P] Create Pydantic user models in `backend/models/user.py`
- [x] T019 [P] Create Pydantic chat models in `backend/models/chat.py`
- [x] T020 Create FastAPI app entry point with CORS in `backend/main.py`
- [x] T021 Create health check endpoint in `backend/main.py`

### Frontend Foundation

- [x] T022 Create BetterAuth client configuration in `src/lib/auth-client.ts`
- [x] T023 [P] Create RAG backend API client in `src/lib/api-client.ts`
- [x] T024 Create AuthContext with useAuth hook in `src/context/AuthContext.tsx`
- [x] T025 [P] Create ChatContext with useChat hook in `src/context/ChatContext.tsx`
- [x] T026 Swizzle Docusaurus Root component to wrap with providers in `src/theme/Root.tsx`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 7 - Book Content Ingestion (Priority: P1) 🎯 MVP Prerequisite

**Goal**: Ingest all textbook markdown files into Qdrant to enable RAG chatbot

**Independent Test**: Run `python scripts/ingest.py` and verify documents appear in Qdrant with embeddings

**Why first**: All RAG features depend on having content indexed. This is a technical prerequisite.

### Implementation for User Story 7

- [x] T027 [US7] Create document chunking utilities with markdown header splitting in `scripts/chunking.py`
- [x] T028 [P] [US7] Create file tracking for incremental ingestion in `scripts/file_tracker.py`
- [x] T029 [US7] Create Qdrant collection setup with vector config in `scripts/ingest.py`
- [x] T030 [US7] Implement embedding generation with OpenAI text-embedding-3-small in `scripts/ingest.py`
- [x] T031 [US7] Implement batch document ingestion with progress output in `scripts/ingest.py`
- [x] T032 [US7] Add incremental ingestion support (detect new/modified files) in `scripts/ingest.py`
- [x] T033 [US7] Run initial ingestion of all docs/ content and verify in Qdrant dashboard

**Checkpoint**: Content is indexed in Qdrant - RAG chatbot can now retrieve relevant content

---

## Phase 4: User Story 1 - User Registration with Background Profile (Priority: P1)

**Goal**: New users can sign up via email/password or OAuth and provide their background during onboarding

**Independent Test**: Complete signup flow, verify background is stored in Neon DB, confirm user sees authenticated state

### Implementation for User Story 1

- [x] T034 [US1] Implement user profile routes (GET/POST /api/user/profile) in `auth-server/src/routes/profile.ts`
- [x] T035 [US1] Add profile routes to Hono app in `auth-server/src/index.ts`
- [x] T036 [US1] Create AuthModal component with email/password form in `src/components/AuthModal/index.tsx`
- [x] T037 [P] [US1] Create AuthModal styles in `src/components/AuthModal/styles.module.css`
- [x] T038 [US1] Add GitHub OAuth button to AuthModal in `src/components/AuthModal/index.tsx`
- [x] T039 [US1] Add Google OAuth button to AuthModal in `src/components/AuthModal/index.tsx`
- [x] T040 [US1] Create OnboardingForm component for background capture in `src/components/OnboardingForm/index.tsx`
- [x] T041 [US1] Implement onboarding flow trigger after first login in `src/context/AuthContext.tsx`
- [x] T042 [US1] Create OAuth callback handler page in `src/pages/auth/callback.tsx`
- [x] T043 [US1] Swizzle Navbar Content to add Login/Signup button in `src/theme/Navbar/Content/index.tsx`

**Checkpoint**: Users can register, provide background, and see authenticated state in navbar

---

## Phase 5: User Story 2 - User Login and Session Management (Priority: P1)

**Goal**: Returning users can log in and maintain sessions across page navigation

**Independent Test**: Log in with valid credentials, refresh page, verify session persists, log out

### Implementation for User Story 2

- [x] T044 [US2] Add login mode to AuthModal component in `src/components/AuthModal/index.tsx`
- [x] T045 [US2] Implement session persistence check on page load in `src/context/AuthContext.tsx`
- [x] T046 [US2] Add logout functionality to AuthContext in `src/context/AuthContext.tsx`
- [x] T047 [US2] Create user dropdown menu in navbar with profile/logout options in `src/theme/Navbar/Content/index.tsx`
- [x] T048 [US2] Create profile settings page for updating background in `src/pages/profile.tsx`

**Checkpoint**: Users can login, see persistent sessions, update profile, and logout

---

## Phase 6: User Story 3 - General RAG Chatbot Interaction (Priority: P1)

**Goal**: Users can ask questions about the textbook and receive grounded AI responses

**Independent Test**: Open chat widget, ask "What is a ROS 2 node?", verify response references textbook content

### Implementation for User Story 3

- [x] T049 [US3] Create RAG agent with search_knowledge_base tool in `backend/agent.py`
- [x] T050 [US3] Implement Qdrant search function with embedding in `backend/rag_service.py`
- [x] T051 [US3] Create conversation memory management in `backend/memory.py`
- [x] T052 [US3] Implement POST /chat endpoint with RAG pipeline in `backend/main.py`
- [x] T053 [US3] Create ChatWidget container component in `src/components/ChatWidget/index.tsx`
- [x] T054 [P] [US3] Create ChatMessage display component in `src/components/ChatWidget/ChatMessage.tsx`
- [x] T055 [P] [US3] Create ChatInput component in `src/components/ChatWidget/ChatInput.tsx`
- [x] T056 [P] [US3] Create ChatWidget styles with floating position in `src/components/ChatWidget/styles.module.css`
- [x] T057 [US3] Add ChatWidget to Root component (appears on all pages) in `src/theme/Root.tsx`
- [x] T058 [US3] Implement source reference display in chat responses in `src/components/ChatWidget/ChatMessage.tsx`
- [x] T059 [US3] Add conversation context persistence within session in `src/context/ChatContext.tsx`

**Checkpoint**: Chat widget works on all pages, retrieves and displays grounded responses with sources

---

## Phase 7: User Story 4 - Context-Aware Chat from Text Selection (Priority: P1)

**Goal**: Users can highlight text and ask questions specifically about that selection

**Independent Test**: Highlight text on a page, click "Ask about this", verify chatbot response is scoped to selection

### Implementation for User Story 4

- [x] T060 [US4] Create TextSelectionHandler component with mouseup listener in `src/components/TextSelectionHandler/index.tsx`
- [x] T061 [US4] Add selection context to ChatContext state in `src/context/ChatContext.tsx`
- [x] T062 [US4] Create "Ask about this selection" popup UI in `src/components/TextSelectionHandler/index.tsx`
- [x] T063 [US4] Modify chat endpoint to accept context_type and context_source in `backend/main.py`
- [x] T064 [US4] Implement context-scoped RAG query in `backend/rag_service.py`
- [x] T065 [US4] Display active context in ChatWidget header in `src/components/ChatWidget/index.tsx`
- [x] T066 [US4] Add "Clear context" button to return to general queries in `src/components/ChatWidget/index.tsx`
- [x] T067 [US4] Add TextSelectionHandler to Root component in `src/theme/Root.tsx`

**Checkpoint**: Text selection triggers context-aware chat with clear UI indication

---

## Phase 8: User Story 5 - Real-Time Urdu Translation (Priority: P2)

**Goal**: Users can translate chapter content to Urdu while preserving code blocks

**Independent Test**: Click "Translate to Urdu" on a chapter, verify prose is translated, code blocks remain in English

### Implementation for User Story 5

- [x] T068 [US5] Create translation service with GPT-4o integration in `backend/translation_service.py`
- [x] T069 [US5] Implement code block preservation in translation prompt in `backend/translation_service.py`
- [x] T070 [US5] Create POST /translate endpoint with caching in `backend/main.py`
- [x] T071 [US5] Create ChapterToolbar component container in `src/components/ChapterToolbar/index.tsx`
- [x] T072 [P] [US5] Create ChapterToolbar styles in `src/components/ChapterToolbar/styles.module.css`
- [x] T073 [US5] Add "Translate to Urdu" button with loading state in `src/components/ChapterToolbar/index.tsx`
- [x] T074 [US5] Implement content replacement with translated text in `src/components/ChapterToolbar/index.tsx`
- [x] T075 [US5] Add "Show Original" button to revert translation in `src/components/ChapterToolbar/index.tsx`
- [x] T076 [US5] Swizzle DocItem to include ChapterToolbar in `src/theme/DocItem/Layout/index.tsx`

**Checkpoint**: Translation button works on all doc pages, preserves code, can toggle back

---

## Phase 9: User Story 6 - Personalized Chapter Content (Priority: P2)

**Goal**: Authenticated users with profiles can personalize chapter content based on their background

**Independent Test**: As user with background, click "Personalize", verify content references stated experience level

### Implementation for User Story 6

- [x] T077 [US6] Create personalization service with GPT-4o integration in `backend/personalization_service.py`
- [x] T078 [US6] Implement profile-based content adaptation prompt in `backend/personalization_service.py`
- [x] T079 [US6] Create POST /personalize endpoint with caching in `backend/main.py`
- [x] T080 [US6] Implement user profile fetch for personalization in `backend/personalization_service.py`
- [x] T081 [US6] Add "Personalize This Chapter" button to ChapterToolbar in `src/components/ChapterToolbar/index.tsx`
- [x] T082 [US6] Add authentication check for personalize button in `src/components/ChapterToolbar/index.tsx`
- [x] T083 [US6] Add profile completion prompt when user hasn't completed onboarding in `src/components/ChapterToolbar/index.tsx`
- [x] T084 [US6] Implement personalized content replacement in `src/components/ChapterToolbar/index.tsx`
- [x] T085 [US6] Add "Show Original" toggle for personalized content in `src/components/ChapterToolbar/index.tsx`

**Checkpoint**: Personalization works for authenticated users with profiles, prompts others to complete profile

---

## Phase 10: Chat History & Persistence (FR-031, FR-032)

**Purpose**: Enable chat history persistence for authenticated users (cross-cutting across chat stories)

- [ ] T086 Implement GET /chat/sessions endpoint for user's sessions in `backend/main.py`
- [ ] T087 Implement GET /chat/sessions/{id} endpoint with messages in `backend/main.py`
- [ ] T088 [P] Implement DELETE /chat/sessions/{id} endpoint in `backend/main.py`
- [ ] T089 Persist chat messages to database in chat endpoint in `backend/main.py`
- [ ] T090 Add chat history panel to ChatWidget in `src/components/ChatWidget/index.tsx`
- [ ] T091 Implement session switching in ChatWidget in `src/components/ChatWidget/index.tsx`
- [ ] T092 Load previous messages when resuming session in `src/context/ChatContext.tsx`

**Checkpoint**: Authenticated users can see and resume previous chat sessions

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, performance, and production readiness

### Error Handling & Resilience

- [ ] T093 [P] Add exponential backoff for OpenAI API calls in `backend/rag_service.py`
- [ ] T094 [P] Add error handling for Qdrant unavailability in `backend/rag_service.py`
- [ ] T095 [P] Add user-friendly error messages in ChatWidget in `src/components/ChatWidget/index.tsx`
- [ ] T096 Add rate limiting handling with queue display in `src/components/ChatWidget/index.tsx`

### Security & Data

- [ ] T097 Implement user data deletion (FR-033) on account delete in `auth-server/src/routes/profile.ts`
- [ ] T098 Add session cleanup cron job query in `auth-server/migrations/cleanup_sessions.sql`

### Performance

- [ ] T099 Add response streaming for long translations in `backend/translation_service.py`
- [ ] T100 Implement translation cache lookup before API call in `backend/translation_service.py`
- [ ] T101 [P] Implement personalization cache lookup in `backend/personalization_service.py`

### Documentation & Validation

- [ ] T102 Update custom.css with chat widget and toolbar styles in `src/css/custom.css`
- [ ] T103 Run full quickstart.md validation checklist
- [ ] T104 Verify all acceptance scenarios from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US7 Ingestion)
                                                    ↓
                          ┌─────────────────────────┴─────────────────────────┐
                          ↓                         ↓                         ↓
                    Phase 4 (US1)              Phase 6 (US3)              Phase 7 (US4)
                    Registration               RAG Chat                  Context Chat
                          ↓                         ↓                         ↓
                    Phase 5 (US2)                   └──────────┬──────────────┘
                    Login/Session                              ↓
                          ↓                              Phase 10
                    Phase 8 (US5)                     Chat History
                    Translation                            ↓
                          ↓                          Phase 11
                    Phase 9 (US6)                      Polish
                    Personalization
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US7 (Ingestion) | Phase 2 | Foundation complete |
| US1 (Registration) | Phase 2 | Foundation complete |
| US2 (Login) | US1 | Registration works |
| US3 (RAG Chat) | US7 | Content indexed |
| US4 (Context Chat) | US3 | Basic chat works |
| US5 (Translation) | Phase 2 | Foundation complete |
| US6 (Personalization) | US1, US5 | Auth + toolbar ready |

### Parallel Opportunities by Phase

**Phase 1**: T001, T002, T003, T004 can all run in parallel (different directories)

**Phase 2**:
- T009, T010, T011 (migrations) in parallel
- T017, T018, T019 (backend) in parallel
- T022, T023, T024, T025 (frontend) in parallel

**Phase 3-7**: Each user story can proceed once dependencies met

**Phase 11**: T093, T094, T095, T100, T101 can run in parallel

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch migration tasks in parallel:
Task: "T009 Create SQL migration 001_create_core_tables.sql"
Task: "T010 Create SQL migration 002_create_chat_tables.sql"
Task: "T011 Create SQL migration 003_create_cache_tables.sql"

# Launch frontend foundation in parallel:
Task: "T022 Create BetterAuth client configuration"
Task: "T023 Create RAG backend API client"
Task: "T024 Create AuthContext"
Task: "T025 Create ChatContext"
```

---

## Implementation Strategy

### MVP First (User Stories 7 + 1 + 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US7 (Ingestion) - **Required for any chat**
4. Complete Phase 4: US1 (Registration) - **Optional for anonymous chat**
5. Complete Phase 6: US3 (RAG Chat)
6. **STOP and VALIDATE**: Basic chat works, can demo
7. Deploy MVP

### Full Feature Delivery

1. MVP (above)
2. Add US2 (Login/Session) - persistence
3. Add US4 (Context Chat) - selection-based
4. Add US5 (Translation) - Urdu support
5. Add US6 (Personalization) - requires auth
6. Add Phase 10 (Chat History) - persistence
7. Complete Phase 11 (Polish)

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 104 |
| **Setup Tasks** | 8 |
| **Foundational Tasks** | 18 |
| **US7 Tasks** (Ingestion) | 7 |
| **US1 Tasks** (Registration) | 10 |
| **US2 Tasks** (Login) | 5 |
| **US3 Tasks** (RAG Chat) | 11 |
| **US4 Tasks** (Context Chat) | 8 |
| **US5 Tasks** (Translation) | 9 |
| **US6 Tasks** (Personalization) | 9 |
| **Chat History Tasks** | 7 |
| **Polish Tasks** | 12 |
| **Parallelizable Tasks** | 34 (marked [P]) |

### MVP Scope

**Minimum Viable Product** = Phase 1 + Phase 2 + Phase 3 (US7) + Phase 6 (US3)
- Total: ~44 tasks
- Delivers: Working RAG chatbot with content indexed
- Add Phase 4 (US1) for authentication: +10 tasks

### Format Validation

- All 104 tasks follow format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- All user story phase tasks have [USx] labels
- All parallelizable tasks marked with [P]
- All tasks include specific file paths
