import sys
import tempfile
import webbrowser
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, Static, DirectoryTree
from textual.containers import VerticalScroll, Horizontal
from textual.reactive import reactive
from textual.binding import Binding
from markdown import markdown

class MarkdownViewerApp(App):
    """A Textual app for viewing Markdown files."""
    
    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }
    
    DirectoryTree {
        width: 30;
        height: 100%;
        dock: left;
        display: none;
        border-right: solid $primary;
    }
    
    DirectoryTree.visible {
        display: block;
    }
    
    #content-area {
        width: 100%;
        height: 100%;
    }
    
    VerticalScroll {
        height: 1fr;
        margin: 1 2;
    }
    
    Markdown {
        margin: 1 2;
    }
    
    Static {
        margin: 1 2;
    }
    """

    BINDINGS = [
        Binding("d", "toggle_dark", "Dark mode", show=True),
        Binding("r", "toggle_raw", "Raw/Rendered", show=True),
        Binding("o", "open_browser", "Open in browser", show=True),
        Binding("f", "toggle_file_tree", "File tree", show=True),
        Binding("q", "quit", "Quit", show=True)
    ]

    # Reactive variables
    show_raw = reactive(False)
    show_file_tree = reactive(False)

    def __init__(self, markdown_path: Path = None):
        super().__init__()
        self.markdown_path = markdown_path
        self.markdown_content = ""
        
        if self.markdown_path and self.markdown_path.exists():
            self.markdown_content = self.markdown_path.read_text()
        elif self.markdown_path:
            self.markdown_content = f"# Error\n\nFile not found: {self.markdown_path}"
        else:
            self.markdown_content = "# Welcome to Markdown Viewer\n\nPlease provide a markdown file as an argument:\n\n```\npython main.py <path_to_markdown_file>\n```\n\nOr press 'f' to open the file tree and browse for markdown files."

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal():
            # File tree panel
            yield DirectoryTree(
                Path.cwd(),
                id="file-tree"
            )
            
            # Main content area
            with VerticalScroll(id="content-area"):
                yield Markdown(self.markdown_content, id="markdown-view")
                yield Static(self.markdown_content, id="raw-view")
        
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the view state when the app mounts."""
        self.update_view()
        self.update_header_title()
        self.update_file_tree_visibility()

    def update_header_title(self) -> None:
        """Update the header title with filename and current mode."""
        mode = "Raw" if self.show_raw else "Rendered"
        if self.markdown_path:
            self.title = f"Markdown Viewer - {self.markdown_path.name} [{mode}]"
        else:
            self.title = f"Markdown Viewer - No file loaded [{mode}]"

    def watch_show_raw(self, show_raw: bool) -> None:
        """React to changes in the show_raw state."""
        self.update_view()
        self.update_header_title()

    def watch_show_file_tree(self, show_file_tree: bool) -> None:
        """React to changes in the show_file_tree state."""
        self.update_file_tree_visibility()

    def update_view(self) -> None:
        """Update which view is displayed based on show_raw state."""
        markdown_view = self.query_one("#markdown-view")
        raw_view = self.query_one("#raw-view")
        
        if self.show_raw:
            markdown_view.display = False
            raw_view.display = True
        else:
            markdown_view.display = True
            raw_view.display = False

    def update_file_tree_visibility(self) -> None:
        """Update the visibility of the file tree panel."""
        file_tree = self.query_one("#file-tree")
        if self.show_file_tree:
            file_tree.add_class("visible")
        else:
            file_tree.remove_class("visible")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection from the directory tree."""
        # Only process markdown files
        if event.path.suffix.lower() in ['.md', '.markdown']:
            self.load_markdown_file(event.path)

    def load_markdown_file(self, path: Path) -> None:
        """Load a markdown file and update the display."""
        try:
            self.markdown_path = path
            self.markdown_content = path.read_text()
            
            # Update both views with new content
            markdown_view = self.query_one("#markdown-view", Markdown)
            raw_view = self.query_one("#raw-view", Static)
            
            markdown_view.update(self.markdown_content)
            raw_view.update(self.markdown_content)
            
            # Update the header
            self.update_header_title()
            
        except Exception as e:
            self.markdown_content = f"# Error\n\nCould not read file: {path}\n\nError: {str(e)}"
            markdown_view = self.query_one("#markdown-view", Markdown)
            raw_view = self.query_one("#raw-view", Static)
            markdown_view.update(self.markdown_content)
            raw_view.update(self.markdown_content)

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

    def action_toggle_raw(self) -> None:
        """Toggle between raw and rendered markdown view."""
        self.show_raw = not self.show_raw

    def action_toggle_file_tree(self) -> None:
        """Toggle the file tree panel."""
        self.show_file_tree = not self.show_file_tree

    def action_open_browser(self) -> None:
        """Open the markdown in the default web browser (respects current view mode)."""
        if self.show_raw:
            # Show raw markdown as plain text
            html_document = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{self.markdown_path.name if self.markdown_path else 'Markdown Viewer'} (Raw)</title>
                <style>
                    body {{
                        font-family: 'Courier New', Courier, monospace;
                        line-height: 1.6;
                        color: #333;
                        max-width: 900px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    pre {{
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        background-color: white;
                        padding: 20px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                    }}
                </style>
            </head>
            <body>
                <pre>{self.markdown_content}</pre>
            </body>
            </html>
            """
        else:
            # Convert markdown to HTML
            html_content = markdown(self.markdown_content)
            
            # Create a complete HTML document with styling
            html_document = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{self.markdown_path.name if self.markdown_path else 'Markdown Viewer'}</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    pre {{
                        background-color: #f0f0f0;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                    code {{
                        background-color: #f0f0f0;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: 'Courier New', Courier, monospace;
                    }}
                    blockquote {{
                        border-left: 4px solid #ddd;
                        margin: 0;
                        padding-left: 20px;
                        color: #666;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #111;
                        margin-top: 24px;
                        margin-bottom: 16px;
                    }}
                    a {{
                        color: #0066cc;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
        
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_file:
            tmp_file.write(html_document)
            tmp_file_path = tmp_file.name
        
        # Open the file in the default browser
        webbrowser.open(f'file://{tmp_file_path}')

if __name__ == "__main__":
    # Check if a markdown file was provided as argument
    if len(sys.argv) > 1:
        markdown_path = Path(sys.argv[1])
    else:
        markdown_path = None
    
    app = MarkdownViewerApp(markdown_path)
    app.run() 