"""
Constants and configuration values for the Markdown Viewer application.
"""

from pathlib import Path

# Application metadata
APP_NAME = "Markdown Viewer"
APP_VERSION = "1.0.0"

# File types
MARKDOWN_EXTENSIONS = ['.md', '.markdown']

# UI dimensions
FILE_TREE_WIDTH = 30
TOC_PANEL_WIDTH = 30

# File watching
FILE_WATCH_INTERVAL = 1.0  # seconds
FILE_WATCH_JOIN_TIMEOUT = 1.0  # seconds

# Search
SEARCH_RESULTS_CAP = 50
SEARCH_PLACEHOLDER = "Search in document... (Enter: next, Shift+Enter: previous, Esc: close)"
SEARCH_NO_MATCHES_PLACEHOLDER = "No matches found - Esc: close"

# Export
EXPORT_DIR_NAME = "exports"
EXPORT_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Notification timers
NOTIFICATION_DURATION = 2.0  # seconds
EXPORT_DIALOG_DURATION = 10.0  # seconds

# Mermaid diagram preview
MERMAID_PREVIEW_LINES = 3
MERMAID_PREVIEW_MAX_LENGTH = 36

# HTML templates
HTML_STYLE = """
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: white;
    }
    pre {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
    code {
        background-color: #f0f0f0;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', Courier, monospace;
    }
    blockquote {
        border-left: 4px solid #ddd;
        margin: 0;
        padding-left: 20px;
        color: #666;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #111;
        margin-top: 24px;
        margin-bottom: 16px;
    }
    a {
        color: #0066cc;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    .mermaid {
        text-align: center;
        margin: 20px 0;
    }
    @media print {
        body {
            background-color: white;
            margin: 0;
            padding: 10mm;
        }
    }
"""

RAW_HTML_STYLE = """
    body {
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.6;
        color: #333;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f5f5f5;
    }
    pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        background-color: white;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
"""

# Default content
DEFAULT_CONTENT = """# Welcome to Markdown Viewer

Please provide a markdown file as an argument:

```
python main.py <path_to_markdown_file>
```

Or press 'f' to open the file tree and browse for markdown files."""

ERROR_CONTENT_TEMPLATE = "# Error\n\n{message}" 