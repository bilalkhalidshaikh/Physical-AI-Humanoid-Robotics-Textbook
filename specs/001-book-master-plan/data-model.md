# Data Model: Book Master Plan

**Feature**: 001-book-master-plan
**Date**: 2025-12-14
**Status**: Complete

## Overview

This documentation project uses a file-based data model. There is no database; all data
is stored in the Git repository as markdown files and JSON configuration files.

## Entities

### Module

A major section of the textbook covering a specific robotics domain.

**Storage**: Directory under `docs/`

**Structure**:
```
docs/<module-name>/
├── _category_.json    # Sidebar configuration
├── index.md           # Module introduction
└── <chapter-n>.md     # Individual chapters
```

**Attributes**:

| Attribute | Type | Location | Description |
|-----------|------|----------|-------------|
| label | string | _category_.json | Display name in sidebar |
| position | number | _category_.json | Order in sidebar (2-5) |
| collapsible | boolean | _category_.json | Whether module can collapse |
| collapsed | boolean | _category_.json | Initial collapsed state |
| description | string | _category_.json link | Brief module description |

**Example** (`_category_.json`):
```json
{
  "label": "Module 1: Robotic Nervous System (ROS 2)",
  "position": 2,
  "collapsible": true,
  "collapsed": false,
  "link": {
    "type": "generated-index",
    "title": "Module 1: Robotic Nervous System (ROS 2)",
    "description": "Learn how robots communicate internally using ROS 2."
  }
}
```

---

### Chapter

A single markdown file within a module covering a specific topic.

**Storage**: Markdown file in module directory

**Attributes**:

| Attribute | Type | Location | Description |
|-----------|------|----------|-------------|
| title | string | frontmatter | Chapter display title |
| sidebar_position | number | frontmatter | Order within module |
| description | string | frontmatter (optional) | SEO description |
| keywords | array | frontmatter (optional) | SEO keywords |
| slug | string | frontmatter (optional) | Custom URL path |

**Example** (frontmatter):
```yaml
---
sidebar_position: 1
title: Introduction to ROS 2
description: Learn the fundamentals of ROS 2 for humanoid robotics
keywords: [ros2, robotics, middleware, communication]
---
```

**Content Structure**:
- H1 heading (main title)
- Overview section
- Learning objectives
- Content sections with code examples
- Physical-First notes (per constitution)
- Exercises/Questions (optional)

---

### Landing Page

The intro.md file serving as the book's homepage and navigation hub.

**Storage**: `docs/intro.md`

**Attributes**:

| Attribute | Type | Location | Description |
|-----------|------|----------|-------------|
| title | string | frontmatter | Page title ("Welcome") |
| sidebar_position | number | frontmatter | Must be 1 (first position) |
| slug | string | frontmatter | Must be "/" for root |

**Example** (frontmatter):
```yaml
---
sidebar_position: 1
title: Welcome
slug: /
---
```

**Required Sections**:
- Welcome message
- Book overview (what you'll learn)
- Learning objectives
- Prerequisites
- Module navigation links

## Relationships

```
Landing Page (intro.md)
    │
    ├── Module 1 (module-1-ros2/)
    │   ├── index.md
    │   └── chapter-*.md
    │
    ├── Module 2 (module-2-digital-twin/)
    │   ├── index.md
    │   └── chapter-*.md
    │
    ├── Module 3 (module-3-brain/)
    │   ├── index.md
    │   └── chapter-*.md
    │
    └── Module 4 (module-4-vla/)
        ├── index.md
        └── chapter-*.md
```

## Validation Rules

### Module Validation

1. Each module MUST have a `_category_.json` file
2. Position values MUST be unique across modules (2, 3, 4, 5)
3. Each module MUST have an `index.md` file
4. Label MUST match the module naming convention from constitution

### Chapter Validation

1. Each chapter MUST have `sidebar_position` in frontmatter
2. Each chapter MUST have `title` in frontmatter
3. Position values MUST be unique within a module
4. Content MUST include Physical-First notes where applicable

### Link Validation

1. All internal links MUST resolve to existing files
2. Module links in intro.md MUST use relative paths: `./module-name/`
3. Cross-module links MUST use relative paths: `../module-name/chapter.md`

## State Transitions

This is a static documentation project. Content has no state transitions.

Future considerations:
- Draft → Published (could use frontmatter `draft: true`)
- Deprecated chapters (could use frontmatter `deprecated: true`)
