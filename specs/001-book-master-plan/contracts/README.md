# Contracts: Book Master Plan

**Feature**: 001-book-master-plan
**Date**: 2025-12-14

## Overview

This feature is a static documentation project using Docusaurus. There are no API
contracts as this is not a backend service.

## Applicable Contracts

### File Structure Contract

The documentation structure follows Docusaurus 3.x conventions:

```
docs/
├── intro.md                    # Landing page (slug: /)
├── module-<n>-<name>/
│   ├── _category_.json         # Sidebar configuration
│   ├── index.md                # Module introduction
│   └── <chapter>.md            # Individual chapters
```

### Frontmatter Contract

All markdown files MUST include:

```yaml
---
sidebar_position: <number>
title: <string>
---
```

### Category JSON Contract

All module folders MUST include `_category_.json`:

```json
{
  "label": "<Module Display Name>",
  "position": <number>,
  "collapsible": true,
  "collapsed": false,
  "link": {
    "type": "generated-index",
    "title": "<Module Title>",
    "description": "<Brief Description>"
  }
}
```

## Future API Contracts

If a chatbot component is added later, API contracts will be defined here for:
- Chat endpoint specification
- RAG query interface
- Content search API
