# Obsurdian

> **Note:** Built with Dash for nested accordion support and Databricks Apps compatibility.

A system engineering documentation portal.

## Features

- Recursive folder navigation
- Dark/light theme toggle
- Auto-numbered headings (Obsidian-style)
- Easy table syntax (`::table`)
- Easy image syntax (`::image`)
- Frontmatter metadata support
- Databricks Apps compatible

## Installation

```bash
cd /Users/bananahq/obsurdian
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Usage

1. Open http://127.0.0.1:8050
2. Browse documents in the sidebar
3. Click any document to view content
4. Toggle theme with the sun/moon icon

## Folder Structure

```
content/
├── Home/
│   └── index.md
├── Systems/
│   └── Braking/
│       ├── overview.md
│       └── ABS/
│           └── diagnostics.md
├── Processes/
│   └── ECR/
│       └── workflow.md
├── Requirements/
│   └── req-001.md
└── Templates/
    └── universal-template.md
```

## How to Add Content

### 1. Add a New Markdown File

Create a `.md` file in `content/` or any subfolder:

```markdown
---
title: My Document
type: System
status: Active
owner: Systems Team
tags:
 - braking
 - safety
---

# My Document

Content goes here...
```

### 2. Add a New Folder

Create a folder in `content/`:
```bash
mkdir -p content/Systems/Braking/ABS
```

### 3. Push to GitHub

```bash
git add .
git commit -m "Add new documentation"
git push
```

## Advanced Features

### Auto-Numbered Headings

Headings are automatically numbered:

```
# Overview
## Purpose
### Signals
```

Becomes:

```
1. Overview
1.1 Purpose
1.1.1 Signals
```

### Easy Table Syntax

```markdown
::table
Field,Value
Owner,Systems Team
Status,Active
::
```

### Easy Image Syntax

```markdown
::image assets/sample-diagram.svg | Sample system diagram | 70%
```

## Environment Variables

- `PORT` - Server port (default: 8050)

## License

MIT
