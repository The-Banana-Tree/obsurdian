# Obsurdian

A system engineering documentation portal built with Dash and Dash Mantine Components.

## Features

- Recursive folder navigation
- Dark/light theme toggle
- Auto-numbered headings
- Easy table syntax (::table)
- Easy image syntax (::image)
- 4+ level nested folders

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Usage

1. Open http://127.0.0.1:8050
2. Navigate through the folder tree on the left
3. Click documents to view content
4. Toggle dark/light theme

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

## License

MIT
