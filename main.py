import sys
import tempfile
import webbrowser
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, Static
from textual.containers import VerticalScroll
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
        Binding("q", "quit", "Quit", show=True)
    ]

    # Reactive variable to track if we're showing raw markdown
    show_raw = reactive(False)

    def __init__(self, markdown_path: Path = None):
        super().__init__()
        self.markdown_path = markdown_path
        self.markdown_content = ""
        
        if self.markdown_path and self.markdown_path.exists():
            self.markdown_content = self.markdown_path.read_text()
        elif self.markdown_path:
            self.markdown_content = f"# Error\n\nFile not found: {self.markdown_path}"
        else:
            self.markdown_content = "# Welcome to Markdown Viewer\n\nPlease provide a markdown file as an argument:\n\n```\npython main.py <path_to_markdown_file>\n```"

    def compose(self) -> ComposeResult:
        # Create header with custom title
        if self.markdown_path:
            header_title = f"Markdown Viewer - {self.markdown_path.name}"
        else:
            header_title = "Markdown Viewer - No file loaded"
        
        yield Header(show_clock=True)
        with VerticalScroll(id="content-container"):
            yield Markdown(self.markdown_content, id="markdown-view")
            yield Static(self.markdown_content, id="raw-view")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the view state when the app mounts."""
        self.update_view()
        # Set the app title which appears in the header
        if self.markdown_path:
            self.title = f"Markdown Viewer - {self.markdown_path.name}"
        else:
            self.title = "Markdown Viewer - No file loaded"

    def watch_show_raw(self, show_raw: bool) -> None:
        """React to changes in the show_raw state."""
        self.update_view()

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

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

    def action_toggle_raw(self) -> None:
        """Toggle between raw and rendered markdown view."""
        self.show_raw = not self.show_raw

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