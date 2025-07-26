"""
CSS styles for the Markdown Viewer application.
"""

from ..constants import FILE_TREE_WIDTH, TOC_PANEL_WIDTH

APP_CSS = f"""
Screen {{
    background: $surface;
}}

#file-tree {{
    display: none;
    width: {FILE_TREE_WIDTH};
    dock: left;
    overflow-y: auto;
}}

#file-tree.visible {{
    display: block;
}}

#toc-panel {{
    display: none;
    width: {TOC_PANEL_WIDTH};
    dock: right;
    overflow-y: auto;
    padding: 1;
}}

#toc-panel.visible {{
    display: block;
}}

Tree {{
    padding: 1;
}}

#content-area {{
    overflow-y: auto;
}}

#main-container {{
    height: 1fr;
}}

#raw-view {{
    display: none;
    padding: 1 2;
}}

#raw-view.visible {{
    display: block;
}}

#markdown-view {{
    display: block;
}}

#markdown-view.hidden {{
    display: none;
}}

VerticalScroll {{
    height: 1fr;
    margin: 1 2;
}}

Markdown {{
    margin: 1 2;
}}

Markdown .search-match {{
    background: yellow;
    color: black;
}}

Markdown .search-match-current {{
    background: #ff6600;
    color: white;
    text-style: bold;
}}

Static {{
    margin: 1 2;
}}

#search-input {{
    dock: top;
    display: none;
    background: $surface-darken-1;
    padding: 0 2;
    margin: 0;
}}

#search-input.visible {{
    display: block;
}}

.search-highlight {{
    background: yellow;
    color: black;
}}

.search-highlight-current {{
    background: orange;
    color: black;
}}
""" 