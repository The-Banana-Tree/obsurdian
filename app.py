import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_mantine_components as dmc
from pathlib import Path
import re
import os
from datetime import datetime

# --- Config ---
APP_NAME = "Obsurdian"
PORT = int(os.environ.get("PORT", 8050))

# --- Metadata Parser ---
def parse_frontmatter(text):
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

# --- Load content ---
def load_content_folder(folder="content"):
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
            content[str(file_path)] = {"metadata": metadata, "content": auto_number_headings(body)}
        except Exception as e:
            print(f"Error: {e}")
    return content, modified_files

# --- Load content ---
content_files, modified_files = load_content_folder()

# --- Dash App ---
app = Dash(__name__, use_pages=False)
app.title = APP_NAME

# --- App Layout ---
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "dark", "fontFamily": "'Inter', sans-serif"},
    children=[
        dmc.AppShell(
            children=[
                dmc.AppShellHeader(
                    children=dmc.Container(
                        fluid=True,
                        children=dmc.Group(
                            justify="space-between",
                            align="center",
                            children=[
                                dmc.Burger(
                                    id="burger-button",
                                    opened=False,
                                    hiddenFrom="sm",
                                    size="sm",
                                ),
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
                ),
                dmc.AppShellNavbar(
                    id="appshell-navbar",
                    p="md",
                    hiddenFrom="sm",
                    children=dmc.ScrollArea(
                        type="auto",
                        offsetScrollbars=True,
                        h="100%",
                        children=[
                            dmc.Text("Navigation", size="sm", fw=700, mt=10, mb=10),
                            dmc.Stack(
                                children=[
                                    dmc.Text(f"📄 {info['metadata'].get('title', k.replace('.md', '').replace('_', ' ').title())}", size="sm")
                                    for k, info in content_files.items()
                                ] if content_files else [dmc.Text("No documents yet")],
                            ),
                            dmc.Divider(my=20),
                            dmc.Text("Recent", size="sm", fw=700, mt=10, mb=10),
                            dmc.List(
                                size="sm",
                                children=[
                                    dmc.ListItem(f"📄 {f['title']} ({f['modified']})")
                                    for f in modified_files[:5]
                                ] if modified_files else [dmc.ListItem("No files yet")],
                            ),
                        ],
                    ),
                ),
                dmc.AppShellMain(
                    children=dmc.Container(
                        fluid=True,
                        p="md",
                        children=[html.Div(id="page-content")],
                    ),
                ),
            ],
            header={"height": 60},
            navbar={"width": 300, "breakpoint": "sm", "collapsed": {"mobile": True}},
        ),
    ],
)

# --- Callbacks ---
@app.callback(Output("appshell-navbar", "hidden"), Input("burger-button", "opened"), State("appshell-navbar", "hidden"))
def toggle_navbar(opened, hidden):
    if opened:
        return not hidden
    return hidden

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if not pathname or pathname == "/":
        folder_count = len(set(k.split("/")[0] for k in content_files.keys() if "/" in k))
        return [
            dmc.Title("Welcome to Obsurdian", order=1, mt=20),
            dmc.Text("Your system engineering documentation portal.", mt=10),
            dmc.Divider(my=20),
            dmc.Grid(
                children=[
                    dmc.Col(dmc.Card(f"{len(content_files)} Documents", mt=10), span=4),
                    dmc.Col(dmc.Card(f"{folder_count} Folders", mt=10), span=4),
                    dmc.Col(dmc.Card("Systems Engineering", mt=10), span=4),
                ],
            ),
        ]
    
    if pathname in content_files:
        info = content_files[pathname]
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
            dmc.Title(metadata.get("title", pathname.replace(".md", "").title()), order=2, mb=20),
            dmc.Stack(children=meta_items, mb=20) if meta_items else None,
            dmc.Divider(my=20),
            dcc.Markdown(content, dangerously_allow_html=True),
        ]
    
    return dmc.Text("Document not found.")

# --- Run server ---
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=PORT, debug=True)
