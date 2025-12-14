# Implementation Plan: Book Master Plan

**Branch**: `001-book-master-plan` | **Date**: 2025-12-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-book-master-plan/spec.md`

## Summary

Create the documentation structure for the Physical AI & Humanoid Robotics textbook using
Docusaurus 3. This includes a landing page (`docs/intro.md`) and four module folders with
proper sidebar configuration for automatic navigation generation.

**Technical Approach**: Use Docusaurus 3.x static site generator with markdown files and
`_category_.json` configurations for hierarchical sidebar organization. Deploy to GitHub
Pages.

## Technical Context

**Language/Version**: JavaScript/TypeScript (Node.js 18+) for Docusaurus, Markdown for content
**Primary Dependencies**: Docusaurus 3.x, React 18, MDX 2.x
**Storage**: Git repository (file-based), GitHub Pages for hosting
**Testing**: Docusaurus build validation, broken link checker (built-in)
**Target Platform**: Static web (GitHub Pages), all modern browsers
**Project Type**: Documentation site (Docusaurus project)
**Performance Goals**: Page load < 3 seconds, Lighthouse score > 90
**Constraints**: Static site only, no server-side processing, GitHub Pages compatible
**Scale/Scope**: 4 modules, ~50+ chapters when complete, single documentation site

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development

| Check | Status | Evidence |
|-------|--------|----------|
| Feature has spec.md before implementation | PASS | `specs/001-book-master-plan/spec.md` created |
| Spec includes acceptance criteria | PASS | 5 user stories with acceptance scenarios |
| Spec includes success metrics | PASS | 5 measurable outcomes (SC-001 to SC-005) |

### II. Physical-First Design

| Check | Status | Evidence |
|-------|--------|----------|
| Examples demonstrate physical constraints | N/A | Documentation structure only - applies to content |
| Simulation content includes reality gap notes | N/A | Placeholder modules created - content to follow |
| Safety considerations documented | PASS | Module index files mention physical-first notes |

### III. Content Accuracy

| Check | Status | Evidence |
|-------|--------|----------|
| Technical claims verifiable | PASS | Docusaurus 3.x conventions verified |
| Version-specific info states version | PASS | Docusaurus 3.x, Node.js 18+ specified |
| Deprecated APIs marked | N/A | No deprecated APIs used |

**Constitution Check Result**: PASS - All applicable gates satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-book-master-plan/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A for docs project)
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
docs/
├── intro.md                    # Landing page (sidebar_position: 1)
├── module-1-ros2/
│   ├── _category_.json         # Sidebar config (position: 2)
│   └── index.md                # Module introduction
├── module-2-digital-twin/
│   ├── _category_.json         # Sidebar config (position: 3)
│   └── index.md
├── module-3-brain/
│   ├── _category_.json         # Sidebar config (position: 4)
│   └── index.md
└── module-4-vla/
    ├── _category_.json         # Sidebar config (position: 5)
    └── index.md
```

**Structure Decision**: Docusaurus documentation site structure selected. The `docs/` folder
contains all content with `_category_.json` files for automatic sidebar generation. No
separate frontend/backend as this is a static documentation site.

## Complexity Tracking

> No constitution violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Implementation Notes

### Docusaurus Setup Requirements (Separate Task)

The following Docusaurus initialization is required before the docs structure is functional:

1. Initialize Docusaurus project: `npx create-docusaurus@latest . classic --typescript`
2. Configure `docusaurus.config.js` for GitHub Pages deployment
3. Set `docs` as the main documentation folder
4. Configure `intro.md` as the docs landing page with `slug: /`

### Files Already Created

The `/sp.specify` command has already created:
- `docs/intro.md` - Landing page with full content
- `docs/module-1-ros2/_category_.json` and `index.md`
- `docs/module-2-digital-twin/_category_.json` and `index.md`
- `docs/module-3-brain/_category_.json` and `index.md`
- `docs/module-4-vla/_category_.json` and `index.md`

### Remaining Tasks

1. Initialize Docusaurus 3 project (creates `package.json`, config files)
2. Run `npm install` to install dependencies
3. Test with `npm run start` for local development
4. Configure GitHub Actions for deployment to GitHub Pages
5. Add chapter content to each module (future specs)
