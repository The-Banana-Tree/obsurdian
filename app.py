import dash
from dash import Dash, html, dcc, Input, Output, State, dash_table, ctx
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from pathlib import Path
import markdown
import re
from datetime import datetime

# --- Config ---
APP_NAME = "Obsurdian"

# --- Metadata Parser ---
def parse_frontmatter(text):
    """Parse YAML frontmatter from markdown text."""
    metadata = {}
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        in_frontmatter = True
        fm_lines = []
        for line in lines[1:]:
            if line.strip() == "---":
                in_frontmatter = False
                break
            fm_lines.append(line)
        
        for line in fm_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "tags":
                    metadata[key] = [t.strip() for t in value.split(",") if t.strip()]
                else:
                    metadata[key] = value
    
    return metadata, text

# --- Auto-number headings ---
def auto_number_headings(text):
    """Convert headings to numbered format."""
    lines = text.splitlines()
    numbers = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    result = []
    
    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.*)$', line)
        if match:
            level = len(match.group(1))
            content = match.group(2)
            
            if re.match(r'^\d+\.\d*\s', content):
                result.append(line)
                continue
            
            numbers[level] += 1
            for lvl in range(level + 1, 7):
                numbers[lvl] = 0
            
            number_parts = [str(numbers[lvl]) for lvl in range(1, level + 1)]
            number_str = ".".join(number_parts)
            result.append(f"{'#' * level} {number_str} {content}")
        else:
            result.append(line)
    
    return "\n".join(result)

# --- Easy tables (::table syntax) ---
def convert_simple_tables(text):
    """Convert ::table blocks to markdown tables."""
    pattern = r'::table\s*(.*?)\s*::'
    
    def replacer(match):
        content = match.group(1).strip()
        lines = [l for l in content.splitlines() if l.strip()]
        if len(lines) < 2:
            return match.group(0)
        
        header = lines[0].split(',')
        rows = [l.split(',') for l in lines[1:]]
        
        table = "| " + " | ".join(header) + " |\n"
        table += "|" + "|".join(["---"] * len(header)) + "|\n"
        for row in rows:
            table += "| " + " | ".join(row) + " |\n"
        return table
    
    return re.sub(pattern, replacer, text, flags=re.DOTALL)

# --- Easy images (::image syntax) ---
def convert_simple_images(text):
    """Convert ::image blocks to HTML img tags."""
    pattern = r'::image\s+([^\|]+)\s*\|\s*([^\|]+)\s*\|\s*([\d%]+)\s*::'
    
    def replacer(match):
        src = match.group(1).strip()
        alt = match.group(2).strip()
        width = match.group(3).strip()
        return f'<img src="{src}" alt="{alt}" style="width:{width}; border-radius:12px;">'
    
    return re.sub(pattern, replacer, text)

# --- Preprocess markdown ---
def preprocess_markdown(text):
    """Apply all markdown preprocessing."""
    text = convert_simple_tables(text)
    text = convert_simple_images(text)
    text = auto_number_headings(text)
    return text

# --- Load content folder ---
def load_content_folder(folder="content"):
    """Load all markdown files from content folder."""
    content = {}
    root_path = Path(folder)
    if not root_path.exists():
        return {}, []
    
    modified_files = []
    for file_path in root_path.rglob("*.md"):
        try:
            text = file_path.read_text()
            metadata, body = parse_frontmatter(text)
            
            modified_files.append({
                "file": str(file_path),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "title": metadata.get("title", file_path.stem.replace("-", " ").title())
            })
            
            content[str(file_path)] = {
                "metadata": metadata,
                "content": preprocess_markdown(body),
            }
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return content, modified_files

# --- Load content ---
content_files, modified_files = load_content_folder()

# --- Dash App ---
app = Dash(
    __name__,
    use_pages=False,
    suppress_callback_exceptions=True,
)

# --- App Layout ---
app.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "dark",
        "fontFamily": "'Inter', sans-serif",
    },
    children=[
        dmc.AppShell(
            header={
                "height": 60,
                "children": [
                    dmc.Container(
                        fluid=True,
                        children=dmc.Group(
                            justify="space-between",
                            align="center",
                            children=[
                                dmc.Title(APP_NAME, order=2),
                                dmc.Switch(
                                    id="theme-switch",
                                    offLabel=html.Span("🌙", style={"fontSize": 18}),
                                    onLabel=html.Span("☀️", style={"fontSize": 18}),
                                    checked=True,
                                ),
                            ],
                        ),
                    ),
                ],
            },
            sidebar={
                "width": 300,
                "breakpoint": "sm",
                "collapsed": {"mobile": True},
                "children": [
                    dmc.ScrollArea(
                        offsetScrollbars=True,
                        children=[
                            dmc.Text("Navigate", size="sm", fw=700, mt=10, mb=10, ml=10),
                            dmc.Accordion(
                                id="folder-accordion",
                                value=["content"],
                                multiple=True,
                                children=[
                                    dmc.AccordionItem(
                                        title="📁 Content",
                                        value="content",
                                        children=[
                                            dmc.Stack(
                                                children=[
                                                    dmc.Accordion(
                                                        value=["root"],
                                                        multiple=True,
                                                        children=[
                                                            dmc.AccordionItem(
                                                                title="📄 Root Documents",
                                                                value="root",
                                                                children=[
                                                                    dmc.Stack(
                                                                        children=[
                                                                            dmc.Anchor(
                                                                                info["metadata"].get("title", k.replace(".md", "").replace("_", " ").title()),
                                                                                href=f"#{k}"
                                                                            )
                                                                            for k, info in content_files.items() if "/" not in k
                                                                        ] if any("/" not in k for k in content_files.keys()) else [dmc.Text("No root documents")],
                                                                    ),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Divider(mY=20),
                            dmc.Text("Recent", size="sm", fw=700, mt=10, mb=10, ml=10),
                            dmc.List(
                                size="sm",
                                children=[
                                    dmc.ListItem(f"📄 {f['title']} ({f['modified']})")
                                    for f in modified_files[:5]
                                ] if modified_files else [dmc.ListItem("No files yet")],
                            ),
                        ],
                    ),
                ],
            },
            main=[
                dmc.Container(
                    fluid=True,
                    p="md",
                    children=[
                        html.Div(id="page-content"),
                    ],
                ),
            ],
        ),
    ],
)

# --- Callbacks ---

@app.callback(
    Output("theme-switch", "checked"),
    Input("theme-switch", "checked"),
)
def update_theme(checked):
    return checked

@app.callback(
    Output("page-content", "children"),
    Input("file-tree", "value"),
)
def render_page(file_path):
    if not file_path:
        folder_count = len(set(k.split("/")[0] for k in content_files.keys() if "/" in k))
        return [
            dmc.Title("Welcome to Obsurdian", order=1, mt=20),
            dmc.Text("Your system engineering documentation portal.", mt=10),
            dmc.Divider(my=20),
            dmc.Grid(
                children=[
                    dmc.Col(dmc.Card(h4=f"{len(content_files)} Documents", mt=10), span=4),
                    dmc.Col(dmc.Card(h4=f"{folder_count} Folders", mt=10), span=4),
                    dmc.Col(dmc.Card(h4=f"Systems Engineering", mt=10), span=4),
                ],
            ),
            dmc.Divider(my=20),
            dmc.Title("Quick Links", order=3),
            dmc.List(
                children=[
                    dmc.ListItem(html.A(f"📄 {info['metadata'].get('title', k.replace('.md', '').replace('_', ' ').title())}", href=f"#{k}"))
                    for k, info in content_files.items() if "/" not in k
                ] if any("/" not in k for k in content_files.keys()) else [dmc.ListItem("No root documents yet")],
            ),
        ]
    
    if file_path in content_files:
        info = content_files[file_path]
        metadata = info["metadata"]
        content = info["content"]
        
        meta_items = []
        if metadata.get("status"):
            meta_items.append(dmc.Badge(metadata["status"], color="green"))
        if metadata.get("owner"):
            meta_items.append(dmc.Badge(metadata["owner"], color="blue"))
        if metadata.get("type"):
            meta_items.append(dmc.Badge(metadata["type"], color="orange"))
        if metadata.get("tags"):
            for tag in metadata["tags"]:
                meta_items.append(dmc.Badge(tag, color="gray"))
        
        return [
            dmc.Title(metadata.get("title", file_path.replace(".md", "").replace("_", " ").title()), order=2, mb=20),
            dmc.Stack(children=meta_items, mb=20) if meta_items else None,
            dmc.Divider(my=20),
            dcc.Markdown(content, dangerously_allow_html=True),
        ]
    
    return dmc.Text("Document not found.")

# --- Run server ---
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
