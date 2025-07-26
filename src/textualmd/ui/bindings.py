"""
Key bindings configuration for the Markdown Viewer application.
"""

from textual.binding import Binding
from typing import List

# Define all application key bindings
APP_BINDINGS: List[Binding] = [
    Binding("d", "toggle_dark", "Dark mode", show=True),
    Binding("r", "toggle_raw", "Raw/Rendered", show=True),
    Binding("o", "open_browser", "Open in browser", show=True),
    Binding("f", "toggle_file_tree", "File tree", show=True),
    Binding("t", "toggle_toc", "Table of contents", show=True),
    Binding("s", "toggle_search", "Search", show=True),
    Binding("e", "export_file", "Export", show=True),
    Binding("q", "quit", "Quit", show=True)
] 