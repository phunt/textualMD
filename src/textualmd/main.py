#!/usr/bin/env python3
"""
Entry point for the Markdown Viewer application.
"""

import sys
from pathlib import Path
from .app import MarkdownViewerApp


def main():
    """Main entry point for the application."""
    # Check if a markdown file was provided as argument
    markdown_path = None
    if len(sys.argv) > 1:
        markdown_path = Path(sys.argv[1])
    
    # Create and run the application
    app = MarkdownViewerApp(markdown_path)
    app.run()


if __name__ == "__main__":
    main() 