# Feature Specification: Interactive RAG Chatbot, Authentication & Localization

**Feature Branch**: `002-chatbot-auth`
**Created**: 2025-12-14
**Status**: Draft
**Input**: User description: "Interactive RAG Chatbot, Authentication & Localization (Hackathon Project 2) - Transform the Docusaurus textbook into an intelligent, personalized AI learning platform with secure login."

## Overview

This feature transforms the Physical AI & Humanoid Robotics textbook into an intelligent, personalized AI learning platform. It combines secure user authentication, a context-aware RAG chatbot, real-time Urdu translation, and personalized content adaptation based on user background.

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React (Docusaurus Swizzled) + OpenAI ChatKit SDK + BetterAuth Client | UI components and chat interface |
| Backend (RAG) | Python FastAPI (`backend/main.py`) + OpenAI Agents SDK | RAG pipeline and AI responses |
| Backend (Auth) | Node.js/Hono (`auth-server/`) + BetterAuth | User authentication and sessions |
| Database | Neon Serverless Postgres | User profiles and chat history |
| Vector DB | Qdrant Cloud Free Tier | Book content embeddings |
| AI Models | OpenAI GPT-4o | RAG responses and translation |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration with Background Profile (Priority: P1)

A new visitor wants to access the AI-powered learning features. They sign up using email/password or social login (GitHub/Google) and provide their software and hardware background during onboarding to enable personalized content.

**Why this priority**: Authentication is the foundation for personalization. The onboarding background capture enables the personalization feature and differentiates this platform from a static textbook.

**Independent Test**: Can be fully tested by completing signup flow, verifying background is captured, and confirming user can access authenticated features.

**Acceptance Scenarios**:

1. **Given** a visitor clicks "Login / Sign Up" in the navbar, **When** they choose to sign up, **Then** they see options for Email/Password registration or Social Login (GitHub/Google).
2. **Given** a visitor completes initial signup credentials, **When** the account is created, **Then** they are presented with an onboarding form asking for their "Software & Hardware Background".
3. **Given** a visitor enters their background (e.g., "I know Python but am new to ROS"), **When** they submit, **Then** this information is stored in their user profile in Neon DB.
4. **Given** a visitor uses GitHub or Google social login, **When** authentication succeeds, **Then** they are also prompted for their background information on first login.
5. **Given** a visitor skips background entry, **When** they proceed, **Then** they can still use the chatbot but personalization features are disabled with a prompt to complete their profile.

---

### User Story 2 - User Login and Session Management (Priority: P1)

A returning user logs in to access their personalized experience, chat history, and continue their learning journey.

**Why this priority**: Login enables returning users to benefit from saved preferences and conversation history, creating continuity in the learning experience.

**Independent Test**: Can be tested by logging in and verifying access to previous chat history and personalization settings.

**Acceptance Scenarios**:

1. **Given** a registered user clicks "Login" in the navbar, **When** they enter valid credentials, **Then** they are authenticated and the navbar shows their profile status.
2. **Given** a user logs in via GitHub or Google, **When** OAuth flow completes, **Then** they are authenticated and can access all features.
3. **Given** an authenticated user refreshes the page, **When** the page reloads, **Then** they remain logged in (session persistence).
4. **Given** a user clicks "Log Out", **When** logout completes, **Then** their session ends and protected features show login prompts.

---

### User Story 3 - General RAG Chatbot Interaction (Priority: P1)

A user wants to ask questions about topics covered anywhere in the textbook. They use the floating chat widget to query the entire book corpus and receive AI-generated answers grounded in the textbook content.

**Why this priority**: The RAG chatbot is the core learning enhancement feature. It transforms passive reading into interactive learning by allowing questions across all modules.

**Independent Test**: Can be tested by opening the chat widget, asking a question about ROS 2 concepts, and verifying the response references relevant textbook content.

**Acceptance Scenarios**:

1. **Given** a user is on any page of the textbook, **When** they look for the chat interface, **Then** they see a floating "Chat with Book" widget.
2. **Given** a user types a general question (e.g., "What is a ROS 2 node?"), **When** they submit, **Then** the chatbot responds with information synthesized from the book content.
3. **Given** the chatbot responds, **When** the user reads the answer, **Then** they see references to relevant sections of the textbook where they can learn more.
4. **Given** a user asks a follow-up question, **When** they submit, **Then** the chatbot maintains conversation context from previous exchanges.

---

### User Story 4 - Context-Aware Chat from Text Selection (Priority: P1)

A user is reading a chapter and encounters a confusing paragraph. They highlight the text and ask questions specifically about that selected content, receiving focused explanations.

**Why this priority**: Context-aware chat dramatically improves learning by allowing users to get clarification on exactly what they're reading, reducing cognitive load and improving comprehension.

**Independent Test**: Can be tested by highlighting text on a page, triggering the chat with selection, and verifying the chatbot response is scoped to the highlighted content.

**Acceptance Scenarios**:

1. **Given** a user highlights text on any page, **When** they release the selection, **Then** a prompt appears offering to "Ask about this selection".
2. **Given** a user clicks "Ask about this selection", **When** the chat opens, **Then** the selected text is automatically included as context in the chat.
3. **Given** a user asks a question about highlighted text, **When** the chatbot responds, **Then** the answer is specifically about the selected content, not the general topic.
4. **Given** a user has highlighted text context, **When** they type a question, **Then** the chat interface clearly shows what text is being used as context.
5. **Given** a user wants to clear the selection context, **When** they click "Clear context" or start a new general chat, **Then** subsequent questions query the full book corpus.

---

### User Story 5 - Real-Time Urdu Translation (Priority: P2)

A user who prefers reading in Urdu wants to translate a chapter. They click "Translate to Urdu" and see the chapter content translated in real-time while preserving technical terms and code blocks.

**Why this priority**: Urdu translation expands accessibility to a significant user base. As a bonus feature, it adds substantial value but the platform functions fully without it.

**Independent Test**: Can be tested by clicking the translate button and verifying the visible content is translated to Urdu while code blocks remain in English.

**Acceptance Scenarios**:

1. **Given** a user is reading any chapter, **When** they look at the top of the page, **Then** they see a "Translate to Urdu" button.
2. **Given** a user clicks "Translate to Urdu", **When** translation begins, **Then** they see a loading indicator while AI processes the content.
3. **Given** translation completes, **When** the user views the page, **Then** prose content is in Urdu while code blocks, commands, and technical terms remain in English.
4. **Given** a user is viewing translated content, **When** they click "Show Original", **Then** the page reverts to the original English content.
5. **Given** a page has images with captions, **When** translation runs, **Then** captions are translated but image content is unchanged.

---

### User Story 6 - Personalized Chapter Content (Priority: P2)

A user with a specific background (e.g., "Python expert, new to robotics") wants the chapter adapted to their level. They click "Personalize This Chapter" and receive content rewritten to leverage their existing knowledge and address their gaps.

**Why this priority**: Personalization is the key differentiator that makes this an intelligent learning platform rather than a static textbook. It requires authentication and background data to function.

**Independent Test**: Can be tested by a user with completed profile clicking personalize, and verifying the rewritten content references their stated background.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a completed background profile is reading a chapter, **When** they look at the top of the page, **Then** they see a "Personalize This Chapter" button.
2. **Given** a user clicks "Personalize This Chapter", **When** the AI processes, **Then** they see a loading indicator while content is being adapted.
3. **Given** a Python-experienced user views a code-heavy chapter, **When** personalization completes, **Then** Python concepts are referenced as "familiar" while new robotics concepts are explained in more detail.
4. **Given** a ROS-experienced user views the ROS 2 module, **When** personalization completes, **Then** basic concepts are summarized briefly while advanced topics receive detailed treatment.
5. **Given** a user without a completed background profile clicks "Personalize", **When** they click the button, **Then** they see a prompt to complete their profile first with a link to profile settings.
6. **Given** a user is viewing personalized content, **When** they click "Show Original", **Then** the page reverts to the standard chapter content.

---

### User Story 7 - Book Content Ingestion (Priority: P1)

A developer or administrator needs to ingest all textbook markdown files into the vector database to enable the RAG chatbot functionality.

**Why this priority**: Without content ingestion, the RAG chatbot has no knowledge base. This is a prerequisite for all chatbot features.

**Independent Test**: Can be tested by running the ingestion script and verifying documents appear in Qdrant with proper embeddings.

**Acceptance Scenarios**:

1. **Given** the `docs/` folder contains markdown files, **When** an admin runs `python scripts/ingest.py`, **Then** all markdown files are processed and embedded.
2. **Given** ingestion runs, **When** processing each file, **Then** the script outputs progress showing which files are being processed.
3. **Given** ingestion completes, **When** checking Qdrant, **Then** each document chunk is stored with its embedding, source file path, and section metadata.
4. **Given** new content is added to `docs/`, **When** ingestion runs again, **Then** only new or modified files are processed (incremental ingestion).

---

### Edge Cases

- What happens when a user highlights text that spans multiple paragraphs or includes code blocks?
  - The full selection is captured as context, with code blocks preserved and clearly delineated in the context sent to the AI.

- How does the system handle chatbot queries when Qdrant is unavailable?
  - Display a friendly error message: "The knowledge base is temporarily unavailable. Please try again shortly." Log the error for monitoring.

- What happens if translation times out on a very long chapter?
  - Implement chunked translation with progressive display. If a chunk fails, show partial translation with an option to retry the remaining content.

- How does personalization handle users who update their background profile?
  - Previously personalized content is marked as "based on previous profile" with an option to re-personalize with updated background.

- What happens when a user tries to personalize without being logged in?
  - The button shows "Login to Personalize" and clicking it redirects to the login flow with a return URL.

- How does the system handle rate limiting from OpenAI API?
  - Implement exponential backoff with user-friendly messages. Queue requests during high load and show estimated wait times.

- What happens to chat history if the user deletes their account?
  - All user data including chat history and profile information is permanently deleted in compliance with data privacy requirements.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication (BetterAuth)**

- **FR-001**: System MUST display a "Login / Sign Up" button in the Docusaurus navbar on all pages.
- **FR-002**: System MUST support user registration via Email/Password authentication.
- **FR-003**: System MUST support social login via GitHub OAuth.
- **FR-004**: System MUST support social login via Google OAuth.
- **FR-005**: System MUST present an onboarding form during first login asking for "Software & Hardware Background".
- **FR-006**: System MUST store user profile data including background information in Neon Postgres.
- **FR-007**: System MUST maintain user sessions across page navigation using BetterAuth session management.
- **FR-008**: System MUST provide logout functionality that invalidates the current session.

**RAG Chatbot**

- **FR-009**: System MUST provide a floating "Chat with Book" widget visible on every page.
- **FR-010**: System MUST process user questions through a RAG pipeline using OpenAI Agents SDK.
- **FR-011**: System MUST retrieve relevant content from Qdrant vector database to ground responses.
- **FR-012**: System MUST maintain conversation context within a chat session.
- **FR-013**: System MUST provide an ingestion script (`scripts/ingest.py`) that processes all `docs/` markdown files.
- **FR-014**: System MUST store document embeddings in Qdrant Cloud with source file metadata.
- **FR-015**: System MUST support incremental ingestion for new or modified content.

**Context-Aware Chat**

- **FR-016**: System MUST detect when a user highlights/selects text on any page.
- **FR-017**: System MUST offer an option to "Ask about this selection" when text is highlighted.
- **FR-018**: System MUST scope chatbot responses to the selected context when context is active.
- **FR-019**: System MUST clearly display the current context in the chat interface.
- **FR-020**: System MUST allow users to clear context and return to general book queries.

**Urdu Translation**

- **FR-021**: System MUST display a "Translate to Urdu" button at the top of every chapter page.
- **FR-022**: System MUST use AI (GPT-4o) to translate prose content to Urdu in real-time.
- **FR-023**: System MUST preserve code blocks, commands, and technical terms in English during translation.
- **FR-024**: System MUST provide a "Show Original" button to revert to English content.
- **FR-025**: System MUST show loading state during translation with progress indication.

**Personalization**

- **FR-026**: System MUST display a "Personalize This Chapter" button for authenticated users with completed profiles.
- **FR-027**: System MUST use the user's stored "Software & Hardware Background" to rewrite chapter content.
- **FR-028**: System MUST adapt explanations based on user's stated experience level with relevant technologies.
- **FR-029**: System MUST provide a "Show Original" button to revert to standard content.
- **FR-030**: System MUST prompt users without completed profiles to add their background before personalizing.

**Chat History & Persistence**

- **FR-031**: System MUST store chat history for authenticated users in Neon Postgres.
- **FR-032**: System MUST allow users to access previous conversations across sessions.
- **FR-033**: System MUST delete all user data when a user deletes their account.

### Key Entities

- **User**: A registered account with email, authentication method (email/password or OAuth provider), creation date, and profile status. Linked to background profile, chat history, and session data.

- **UserProfile**: Extended user information including "Software & Hardware Background" text, preferred language, and personalization preferences. One-to-one relationship with User.

- **ChatSession**: A conversation thread belonging to a user, with creation timestamp, last activity, and optional context reference (selected text). Contains ordered messages.

- **ChatMessage**: An individual message within a session, with role (user/assistant), content, timestamp, and optional source references for RAG responses.

- **DocumentChunk**: A segment of textbook content stored in Qdrant, with embedding vector, source file path, section heading, and chunk position for retrieval.

- **TranslationCache**: Cached Urdu translations of chapters to avoid redundant API calls, with chapter identifier, translation content, and cache timestamp.

## Assumptions

- OpenAI API access is available with sufficient quota for GPT-4o usage (chat, translation, personalization).
- Qdrant Cloud Free Tier provides adequate storage and query capacity for the textbook content (estimated <100MB embeddings).
- Neon Serverless Postgres Free Tier is sufficient for user profiles and chat history storage.
- BetterAuth supports the required OAuth providers (GitHub, Google) with standard configuration.
- Users have modern browsers supporting text selection detection and web standards.
- The Docusaurus site can be extended via swizzled components without breaking the documentation build.
- Network latency for AI operations is acceptable for educational use (responses within 10-15 seconds).
- Urdu translations of technical content are linguistically valid even when preserving English technical terms.

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Authentication**

- **SC-001**: Users can complete registration (email or social) in under 2 minutes.
- **SC-002**: Users can complete the background onboarding form in under 1 minute.
- **SC-003**: Login succeeds within 5 seconds for returning users.
- **SC-004**: 100% of authenticated features are inaccessible to unauthenticated users.

**RAG Chatbot**

- **SC-005**: Chatbot responds to general questions within 10 seconds.
- **SC-006**: 90% of chatbot responses include relevant references to textbook sections.
- **SC-007**: Users can access the chat widget on every page of the textbook.
- **SC-008**: Content ingestion processes all markdown files with zero data loss.

**Context-Aware Chat**

- **SC-009**: Text selection detection works within 500ms of selection completion.
- **SC-010**: Context-scoped responses are demonstrably relevant to the selected text (not generic).
- **SC-011**: Users can switch between context and general modes without page refresh.

**Translation**

- **SC-012**: Translation completes for average chapter length (2000 words) within 30 seconds.
- **SC-013**: Code blocks and technical terms remain in English after translation (100% preservation).
- **SC-014**: Users can toggle between Urdu and English without data loss.

**Personalization**

- **SC-015**: Personalized content reflects the user's stated background in at least 3 observable ways per chapter.
- **SC-016**: Personalization completes for average chapter within 45 seconds.
- **SC-017**: Users without profiles are clearly guided to complete their background before personalizing.

**Overall Platform**

- **SC-018**: System supports 50 concurrent users without degradation.
- **SC-019**: Chat history persists across sessions with zero data loss for authenticated users.
- **SC-020**: All user data is deleted within 24 hours of account deletion request.
