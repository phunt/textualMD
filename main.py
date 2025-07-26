import sys
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, Static
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.binding import Binding

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
        yield Header()
        with VerticalScroll(id="content-container"):
            yield Markdown(self.markdown_content, id="markdown-view")
            yield Static(self.markdown_content, id="raw-view")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the view state when the app mounts."""
        self.update_view()

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

if __name__ == "__main__":
    # Check if a markdown file was provided as argument
    if len(sys.argv) > 1:
        markdown_path = Path(sys.argv[1])
    else:
        markdown_path = None
    
    app = MarkdownViewerApp(markdown_path)
    app.run() 