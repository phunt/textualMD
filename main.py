import sys
import tempfile
import webbrowser
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, Static, DirectoryTree, Input
from textual.containers import VerticalScroll, Horizontal
from textual.reactive import reactive
from textual.binding import Binding
from markdown import markdown
from rich.text import Text
from rich.syntax import Syntax
import re

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
    
    #main-container {
        height: 1fr;
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
    
    Markdown .search-match {
        background: yellow;
        color: black;
    }
    
    Markdown .search-match-current {
        background: #ff6600;
        color: white;
        text-style: bold;
    }
    
    Static {
        margin: 1 2;
    }
    
    #search-input {
        dock: top;
        display: none;
        background: $surface-darken-1;
        padding: 0 2;
        margin: 0;
    }
    
    #search-input.visible {
        display: block;
    }
    
    .search-highlight {
        background: yellow;
        color: black;
    }
    
    .search-highlight-current {
        background: orange;
        color: black;
    }
    """

    BINDINGS = [
        Binding("d", "toggle_dark", "Dark mode", show=True),
        Binding("r", "toggle_raw", "Raw/Rendered", show=True),
        Binding("o", "open_browser", "Open in browser", show=True),
        Binding("f", "toggle_file_tree", "File tree", show=True),
        Binding("s", "toggle_search", "Search", show=True),
        Binding("q", "quit", "Quit", show=True)
    ]

    # Reactive variables
    show_raw = reactive(False)
    show_file_tree = reactive(False)
    show_search = reactive(False)
    search_term = reactive("")
    search_results = reactive(list, recompose=False)
    current_search_index = reactive(0)

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
        
        # Don't include search input in initial compose - will add dynamically
        
        with Horizontal(id="main-container"):
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
        # Don't update visibility on mount - let the CSS handle initial state
        # The reactive variables are already False by default
        
        # Focus the main content area to ensure footer is visible
        # and we're not in search mode by default
        if self.show_raw:
            raw_view = self.query_one("#raw-view", Static)
            raw_view.focus()
        else:
            markdown_view = self.query_one("#markdown-view", Markdown)
            markdown_view.focus()

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
        # Update search highlights if search is active
        if self.search_term:
            self.update_search_highlights()

    def watch_show_file_tree(self, show_file_tree: bool) -> None:
        """React to changes in the show_file_tree state."""
        self.update_file_tree_visibility()

    def watch_show_search(self, show_search: bool) -> None:
        """React to changes in the show_search state."""
        if show_search:
            # Mount the search input dynamically
            search_input = Input(
                placeholder="Search in document... (Enter: next, Shift+Enter: previous, Esc: close)", 
                id="search-input"
            )
            # Mount it after the header
            header = self.query_one(Header)
            self.mount(search_input, after=header)
            # Apply the visible class and focus
            search_input.add_class("visible")
            search_input.focus()
        else:
            # Remove the search input if it exists
            try:
                search_input = self.query_one("#search-input", Input)
                search_input.remove()
                # Clear search state
                self.search_term = ""
                self.search_results = []
                self.current_search_index = 0
                self.update_search_highlights()
                
                # Reset both views to original content
                markdown_view = self.query_one("#markdown-view", Markdown)
                raw_view = self.query_one("#raw-view", Static)
                markdown_view.update(self.markdown_content)
                raw_view.update(self.markdown_content)
                
                # Focus back on content
                if self.show_raw:
                    raw_view.focus()
                else:
                    markdown_view.focus()
            except:
                pass  # Search input doesn't exist

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

    def update_search_visibility(self) -> None:
        """Update the visibility of the search panel."""
        # This method is no longer needed since we mount/unmount dynamically
        pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_term = event.value
            self.perform_search()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in search input - go to next result."""
        if event.input.id == "search-input" and self.search_results:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.update_search_highlights()
            self.scroll_to_current_result()

    def on_key(self, event) -> None:
        """Handle key events."""
        if self.show_search:
            if event.key == "escape":
                self.show_search = False
                event.prevent_default()
            elif event.key == "shift+enter" and self.search_results:
                # Go to previous result
                self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
                self.update_search_highlights()
                self.scroll_to_current_result()
                event.prevent_default()

    def perform_search(self) -> None:
        """Perform search in the current content."""
        if not self.search_term:
            self.search_results = []
            self.current_search_index = 0
            self.update_search_highlights()
            return
        
        # Find all matches in the content
        pattern = re.escape(self.search_term)
        matches = list(re.finditer(pattern, self.markdown_content, re.IGNORECASE))
        
        self.search_results = [(m.start(), m.end()) for m in matches]
        self.current_search_index = 0 if self.search_results else -1
        
        self.update_search_highlights()
        if self.search_results:
            self.scroll_to_current_result()
        
        # Update search input placeholder with results count
        try:
            search_input = self.query_one("#search-input", Input)
            if self.search_results:
                count = len(self.search_results)
                current = self.current_search_index + 1
                search_input.placeholder = f"Search ({current}/{count} matches) - Enter: next, Shift+Enter: previous, Esc: close"
            else:
                search_input.placeholder = "No matches found - Esc: close"
        except:
            pass  # Search input doesn't exist

    def update_search_highlights(self) -> None:
        """Update the display to highlight search results."""
        # Update the subtitle to show search status
        if self.search_results:
            count = len(self.search_results)
            current = self.current_search_index + 1
            self.sub_title = f"Search: {self.search_term} ({current}/{count})"
        elif self.search_term:
            self.sub_title = f"Search: {self.search_term} (no matches)"
        else:
            self.sub_title = ""
        
        # Update the content display with highlights
        if self.search_term or self.search_results:
            if self.show_raw:
                self.update_raw_view_with_highlights()
            else:
                self.update_markdown_view_with_highlights()
        else:
            # Reset to plain content if no search
            if self.show_raw:
                raw_view = self.query_one("#raw-view", Static)
                raw_view.update(self.markdown_content)
            else:
                markdown_view = self.query_one("#markdown-view", Markdown)
                markdown_view.update(self.markdown_content)

    def update_markdown_view_with_highlights(self) -> None:
        """Update the markdown view with search highlights."""
        markdown_view = self.query_one("#markdown-view", Markdown)
        
        if not self.search_results:
            markdown_view.update(self.markdown_content)
            return
        
        # Create highlighted content using unicode markers
        highlighted_content = self.markdown_content
        
        # Sort results by position in reverse order to avoid offset issues
        sorted_results = sorted(enumerate(self.search_results), key=lambda x: x[1][0], reverse=True)
        
        # Apply visual highlighting with unicode characters
        for i, (start, end) in sorted_results:
            match_text = highlighted_content[start:end]
            
            if i == self.current_search_index:
                # Current match - use distinctive markers
                replacement = f'【{match_text}】'
            else:
                # Other matches - use lighter markers
                replacement = f'〖{match_text}〗'
            
            highlighted_content = highlighted_content[:start] + replacement + highlighted_content[end:]
        
        # Update the markdown view with highlighted content
        markdown_view.update(highlighted_content)

    def update_raw_view_with_highlights(self) -> None:
        """Update the raw view with search highlights."""
        raw_view = self.query_one("#raw-view", Static)
        
        if not self.search_results:
            raw_view.update(self.markdown_content)
            return
        
        # Create a Rich Text object with the content
        text = Text(self.markdown_content)
        
        # Apply highlighting to all matches
        for i, (start, end) in enumerate(self.search_results):
            if i == self.current_search_index:
                # Current match - use orange background
                text.stylize("bold yellow on dark_orange", start, end)
            else:
                # Other matches - use yellow background
                text.stylize("black on yellow", start, end)
        
        # Update the raw view with the highlighted text
        raw_view.update(text)

    def scroll_to_current_result(self) -> None:
        """Scroll to the current search result."""
        if self.search_results and 0 <= self.current_search_index < len(self.search_results):
            # Get the current result position
            start, end = self.search_results[self.current_search_index]
            
            # Calculate line number
            lines_before = self.markdown_content[:start].count('\n')
            
            # Get the appropriate view widget
            if self.show_raw:
                view_widget = self.query_one("#raw-view", Static)
            else:
                view_widget = self.query_one("#markdown-view", Markdown)
            
            # Get the scrollable container
            scroll_container = self.query_one("#content-area", VerticalScroll)
            
            # Calculate approximate scroll position
            # This is a rough estimate - each line is approximately 1 unit high
            try:
                # Scroll to put the match in the middle of the view
                viewport_height = scroll_container.size.height
                target_y = max(0, lines_before - viewport_height // 2)
                scroll_container.scroll_to(y=target_y, animate=False)
            except:
                # If scrolling fails, just log it
                self.log(f"Would scroll to line {lines_before}")

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
            
            # Clear search if active
            if self.show_search:
                self.search_term = ""
                self.search_results = []
                self.current_search_index = 0
                self.perform_search()
            
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

    def action_toggle_search(self) -> None:
        """Toggle the search panel."""
        self.show_search = not self.show_search

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