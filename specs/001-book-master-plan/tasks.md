# Tasks: Book Master Plan

**Input**: Design documents from `/specs/001-book-master-plan/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No tests explicitly requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project root**: Repository root directory
- **Docs content**: `docs/` folder (already created)
- **Config files**: Root level (`docusaurus.config.ts`, `package.json`, etc.)

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize Docusaurus project and basic configuration

- [x] T001 Initialize Docusaurus 3 project with TypeScript template at repository root
- [x] T002 [P] Configure package.json with project name "physical-ai-book"
- [x] T003 [P] Remove default Docusaurus docs content (blog/, default docs)
- [x] T004 Preserve existing docs/ folder content during Docusaurus setup

**Checkpoint**: Docusaurus project initialized with existing docs content preserved

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before user stories can be validated

**CRITICAL**: No user story validation can proceed until this phase is complete

- [x] T005 Configure docusaurus.config.ts with GitHub Pages settings in docusaurus.config.ts
- [x] T006 [P] Configure docs plugin to serve from root URL (routeBasePath: '/') in docusaurus.config.ts
- [x] T007 [P] Set onBrokenLinks: 'throw' for strict link validation in docusaurus.config.ts
- [x] T008 [P] Configure sidebar auto-generation in sidebars.ts
- [x] T009 Install dependencies with npm install at repository root
- [x] T010 Verify development server starts with npm run start

**Checkpoint**: Foundation ready - Docusaurus serves docs content locally

---

## Phase 3: User Story 1 - Navigate Textbook Landing Page (Priority: P1)

**Goal**: Readers can visit the landing page and see book overview with module navigation

**Independent Test**: Visit http://localhost:3000/ and verify landing page displays with module links

### Implementation for User Story 1

- [x] T011 [US1] Verify docs/intro.md has correct frontmatter (slug: /, sidebar_position: 1)
- [x] T012 [US1] Verify landing page displays welcome message and book overview
- [x] T013 [US1] Verify landing page includes learning objectives section
- [x] T014 [US1] Verify landing page includes prerequisites section
- [x] T015 [US1] Verify all four module links work from landing page in docs/intro.md
- [x] T016 [US1] Test navigation from landing page to each module (2 clicks or fewer)

**Checkpoint**: User Story 1 complete - Landing page fully functional

---

## Phase 4: User Story 2 - Access Module 1: ROS 2 (Priority: P2)

**Goal**: Readers can navigate to Module 1 and see ROS 2 content overview

**Independent Test**: Click Module 1 link from landing page, verify module index loads

### Implementation for User Story 2

- [x] T017 [P] [US2] Verify docs/module-1-ros2/_category_.json has correct position (2)
- [x] T018 [P] [US2] Verify docs/module-1-ros2/index.md has proper frontmatter
- [x] T019 [US2] Verify Module 1 appears in sidebar with correct label
- [x] T020 [US2] Test adding a sample chapter to verify auto-sidebar works in docs/module-1-ros2/

**Checkpoint**: User Story 2 complete - Module 1 accessible and extensible

---

## Phase 5: User Story 3 - Access Module 2: Digital Twin (Priority: P2)

**Goal**: Readers can navigate to Module 2 and see Gazebo/Digital Twin content overview

**Independent Test**: Click Module 2 link from landing page, verify module index loads

### Implementation for User Story 3

- [x] T021 [P] [US3] Verify docs/module-2-digital-twin/_category_.json has correct position (3)
- [x] T022 [P] [US3] Verify docs/module-2-digital-twin/index.md has proper frontmatter
- [x] T023 [US3] Verify Module 2 appears in sidebar with correct label
- [x] T024 [US3] Test navigation from Module 1 to Module 2 via sidebar

**Checkpoint**: User Story 3 complete - Module 2 accessible

---

## Phase 6: User Story 4 - Access Module 3: AI-Robot Brain (Priority: P2)

**Goal**: Readers can navigate to Module 3 and see Isaac Sim/AI content overview

**Independent Test**: Click Module 3 link from landing page, verify module index loads

### Implementation for User Story 4

- [x] T025 [P] [US4] Verify docs/module-3-brain/_category_.json has correct position (4)
- [x] T026 [P] [US4] Verify docs/module-3-brain/index.md has proper frontmatter
- [x] T027 [US4] Verify Module 3 appears in sidebar with correct label
- [x] T028 [US4] Test sidebar collapse/expand functionality for Module 3

**Checkpoint**: User Story 4 complete - Module 3 accessible

---

## Phase 7: User Story 5 - Access Module 4: VLA (Priority: P2)

**Goal**: Readers can navigate to Module 4 and see Vision-Language-Action content overview

**Independent Test**: Click Module 4 link from landing page, verify module index loads

### Implementation for User Story 5

- [x] T029 [P] [US5] Verify docs/module-4-vla/_category_.json has correct position (5)
- [x] T030 [P] [US5] Verify docs/module-4-vla/index.md has proper frontmatter
- [x] T031 [US5] Verify Module 4 appears in sidebar with correct label
- [x] T032 [US5] Verify all modules appear in correct order (1, 2, 3, 4) in sidebar

**Checkpoint**: User Story 5 complete - All modules accessible

---

## Phase 8: Polish & Deployment

**Purpose**: Production build, deployment configuration, and final validation

- [x] T033 [P] Run npm run build and verify zero broken link errors
- [x] T034 [P] Create GitHub Actions workflow in .github/workflows/deploy.yml
- [ ] T035 Configure GitHub Pages in repository settings
- [ ] T036 Deploy to GitHub Pages and verify live site
- [x] T037 Validate all success criteria (SC-001 through SC-005)
- [x] T038 Run quickstart.md validation checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1) should complete first as it validates the landing page
  - US2-US5 (P2) can proceed in parallel after US1 or sequentially
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Primary entry point
- **User Story 2 (P2)**: Can start after US1 - Independent module
- **User Story 3 (P2)**: Can start after US1 - Independent module
- **User Story 4 (P2)**: Can start after US1 - Independent module
- **User Story 5 (P2)**: Can start after US1 - Independent module

### Parallel Opportunities

- T002, T003 can run in parallel (different concerns)
- T006, T007, T008 can run in parallel (different config sections)
- T017, T018 can run in parallel (different files)
- T021, T022 can run in parallel (different files)
- T025, T026 can run in parallel (different files)
- T029, T030 can run in parallel (different files)
- T033, T034 can run in parallel (build vs workflow)

---

## Parallel Example: Foundational Phase

```bash
# Launch config tasks in parallel:
Task: "Configure docs plugin to serve from root URL in docusaurus.config.ts"
Task: "Set onBrokenLinks: 'throw' for strict link validation in docusaurus.config.ts"
Task: "Configure sidebar auto-generation in sidebars.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T010)
3. Complete Phase 3: User Story 1 (T011-T016)
4. **STOP and VALIDATE**: Test landing page independently
5. Deploy/demo if ready - readers can see the book introduction

### Incremental Delivery

1. Setup + Foundational → Docusaurus running locally
2. User Story 1 → Landing page functional → Deploy preview
3. User Story 2-5 → Each module accessible → Deploy updates
4. Polish → Production deployment with CI/CD

### Suggested MVP Scope

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1)**

This delivers:
- Functional Docusaurus site
- Complete landing page with book overview
- Navigation links to all modules (even if module content is placeholder)
- Local development environment working

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Most content files already created by /sp.specify
- Primary work is Docusaurus configuration and validation
- No automated tests required (manual validation per spec)
- Commit after each phase completion for incremental progress

## Implementation Status

**Completed**: 2025-12-14
**Tasks Completed**: 36/38 (95%)
**Remaining**: T035, T036 (GitHub Pages configuration - requires repository push)
