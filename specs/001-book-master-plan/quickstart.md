# Quickstart: Book Master Plan

**Feature**: 001-book-master-plan
**Date**: 2025-12-14

## Prerequisites

Before you begin, ensure you have:

- Node.js 18+ installed (`node --version`)
- npm 9+ installed (`npm --version`)
- Git configured with your GitHub credentials

## Setup Steps

### 1. Initialize Docusaurus Project

From the repository root, run:

```bash
# Initialize Docusaurus in current directory
npx create-docusaurus@latest . classic --typescript

# When prompted about overwriting existing files, select:
# - Keep existing docs/ folder (contains our content)
# - Overwrite other files as needed
```

**Note**: Since we already have a `docs/` folder with content, you may need to:
1. Temporarily rename `docs/` to `docs-backup/`
2. Run the Docusaurus init
3. Move content back from `docs-backup/` to `docs/`

### 2. Configure for GitHub Pages

Edit `docusaurus.config.js`:

```javascript
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A comprehensive textbook on building intelligent humanoid robots',
  favicon: 'img/favicon.ico',

  // GitHub Pages configuration
  url: 'https://<your-username>.github.io',
  baseUrl: '/Physical-AI-Book/',
  organizationName: '<your-username>',
  projectName: 'Physical-AI-Book',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  // Strict link checking
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'throw',

  // ... rest of config
};
```

### 3. Configure Docs as Main Content

In `docusaurus.config.js`, update the docs plugin:

```javascript
docs: {
  sidebarPath: './sidebars.js',
  routeBasePath: '/', // Docs at root instead of /docs
  editUrl: 'https://github.com/<username>/Physical-AI-Book/edit/main/',
},
```

### 4. Install Dependencies

```bash
npm install
```

### 5. Start Development Server

```bash
npm run start
```

The site should open at `http://localhost:3000/Physical-AI-Book/`

### 6. Verify Content Structure

After starting the dev server, verify:

- [ ] Landing page displays at root URL
- [ ] All 4 modules appear in sidebar
- [ ] Module links work from landing page
- [ ] Module index pages display correctly
- [ ] Sidebar collapses/expands properly

### 7. Build for Production

```bash
npm run build
```

This should complete with no errors if all links are valid.

### 8. Deploy to GitHub Pages

```bash
# Using Docusaurus deploy command
GIT_USER=<your-username> npm run deploy

# Or configure GitHub Actions (recommended)
```

## GitHub Actions Deployment

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build website
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: build

      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

## Adding New Content

### Add a New Chapter

1. Create markdown file in the appropriate module folder:

```bash
touch docs/module-1-ros2/02-nodes.md
```

2. Add frontmatter:

```yaml
---
sidebar_position: 2
title: Understanding ROS 2 Nodes
---

# Understanding ROS 2 Nodes

Your content here...
```

3. The sidebar updates automatically on next build.

### Add a New Module

1. Create module directory:

```bash
mkdir docs/module-5-new
```

2. Create `_category_.json`:

```json
{
  "label": "Module 5: New Module",
  "position": 6,
  "collapsible": true,
  "collapsed": false
}
```

3. Create `index.md` with introduction content.

## Troubleshooting

### Broken Links Error

If build fails with broken links:

1. Check the error message for the broken path
2. Verify the file exists at that path
3. Ensure relative paths are correct (`./` for same directory, `../` for parent)

### Sidebar Not Updating

1. Restart the dev server
2. Clear `.docusaurus` cache: `rm -rf .docusaurus`
3. Verify `_category_.json` syntax is valid JSON

### GitHub Pages 404

1. Verify `baseUrl` in config matches repository name
2. Check that `gh-pages` branch exists
3. Verify GitHub Pages is enabled in repository settings
