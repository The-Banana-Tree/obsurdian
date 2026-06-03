#!/usr/bin/env python3
"""Obsurdian - System Documentation Portal (Streamlit + Databricks Apps)"""

import streamlit as st
from pathlib import Path
import re
import os
from datetime import datetime

# --- Config ---
APP_NAME = "Obsurdian"
PORT = int(os.environ.get("STREAMLIT_SERVER_PORT", 8501))

# --- Page Config ---
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            st.error(f"Error loading {file_path}: {e}")
    return content, modified_files

# --- Load content ---
content_files, modified_files = load_content_folder()

# --- Sidebar ---
with st.sidebar:
    st.header(f"🤖 {APP_NAME}")
    st.divider()
    
    st.subheader("📄 Documents")
    for path, info in content_files.items():
        title = info["metadata"].get("title", path.replace(".md", "").replace("_", " ").title())
        st.page_link("app.py", label=f"📄 {title}", disabled=True if path != st.query_params.get("page", "") else False)
    
    if modified_files:
        st.divider()
        st.subheader("⏰ Recent")
        for f in modified_files[:5]:
            st.caption(f"• {f['title']} ({f['modified']})")

# --- Main Content ---
st.title(APP_NAME)
st.markdown("Your system engineering documentation portal.")

# --- Stats Cards ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Documents", len(content_files))
with col2:
    folder_count = len(set(k.split("/")[0] for k in content_files.keys() if "/" in k))
    st.metric("Folders", folder_count)
with col3:
    st.metric("System Engineering", "Active")

st.divider()

# --- Route to document or home ---
if st.query_params.get("page"):
    pathname = st.query_params.get("page")
    if pathname in content_files:
        info = content_files[pathname]
        metadata = info["metadata"]
        content = info["content"]
        
        st.header(metadata.get("title", pathname.replace(".md", "").title()))
        
        meta_items = []
        if metadata.get("status"):
            meta_items.append(f":green[{metadata['status']}]")
        if metadata.get("owner"):
            meta_items.append(f":blue[{metadata['owner']}]")
        if metadata.get("type"):
            meta_items.append(f":orange[{metadata['type']}]")
        if metadata.get("tags"):
            for tag in metadata["tags"]:
                meta_items.append(f":gray[{tag}]")
        
        if meta_items:
            st.markdown(" | ".join(meta_items))
        
        st.divider()
        st.markdown(content)
