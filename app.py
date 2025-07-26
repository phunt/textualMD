"""
Main application module for the Markdown Viewer.
"""

import tempfile
import webbrowser
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Markdown, Static, DirectoryTree, Input, Tree
from textual.containers import VerticalScroll, Horizontal
from textual.reactive import reactive
from textual.events import Key
from rich.text import Text
from rich.markup import escape

from constants import (
    APP_NAME,
    DEFAULT_CONTENT,
    NOTIFICATION_DURATION,
    EXPORT_DIALOG_DURATION,
    SEARCH_PLACEHOLDER,
    SEARCH_NO_MATCHES_PLACEHOLDER
)
from ui import APP_CSS, APP_BINDINGS, UIHelper
from services import (
    FileManager,
    FileWatcher,
    MarkdownProcessor,
    SearchEngine,
    ExportManager
)


class MarkdownViewerApp(App):
    """A Textual app for viewing Markdown files."""
    
    CSS = APP_CSS
    BINDINGS = APP_BINDINGS

    # Reactive variables
    show_raw = reactive(False)
    show_file_tree = reactive(False)
    show_toc = reactive(False)
    show_search = reactive(False)

    def __init__(self, markdown_path: Optional[Path] = None):
        """
        Initialize the Markdown Viewer application.
        
        Args:
            markdown_path: Optional path to a markdown file to load
        """
        super().__init__()
        
        # Initialize services
        self.file_manager = FileManager()
        self.markdown_processor = MarkdownProcessor()
        self.search_engine = SearchEngine()
        self.export_manager = ExportManager()
        self.file_watcher = FileWatcher(self._on_file_changed)
        
        # UI helper
        self.ui_helper = UIHelper()
        
        # Application state
        self.markdown_content = ""
        self._export_html_path: Optional[Path] = None
        self._original_content: Optional[str] = None
        self._original_path: Optional[Path] = None
        
        # Load initial file if provided
        if markdown_path:
            self._load_initial_file(markdown_path)
        else:
            self.markdown_content = DEFAULT_CONTENT

    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        yield Header(show_clock=True)
        
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
            
            # Table of contents panel
            with VerticalScroll(id="toc-panel"):
                yield Tree("Table of Contents", id="toc-tree")
        
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the view state when the app mounts."""
        self._update_view()
        self._update_header_title()
        self._build_table_of_contents()
        
        # Start file watching if we have a file
        if self.file_manager.current_file:
            self.file_watcher.start(self.file_manager.current_file)
        
        # Focus the main content area
        self._focus_content_area()
        
        # Process markdown for Mermaid diagrams
        if not self.show_raw:
            self._update_markdown_view()

    def on_unmount(self) -> None:
        """Clean up when the app exits."""
        self.file_watcher.stop()

    # Reactive watchers
    def watch_show_raw(self, show_raw: bool) -> None:
        """React to changes in the show_raw state."""
        self._update_view()
        self._update_header_title()
        if self.search_engine.search_term:
            self._update_search_highlights()

    def watch_show_file_tree(self, show_file_tree: bool) -> None:
        """React to changes in the show_file_tree state."""
        file_tree = self.query_one("#file-tree")
        if show_file_tree:
            file_tree.add_class("visible")
        else:
            file_tree.remove_class("visible")

    def watch_show_toc(self, show_toc: bool) -> None:
        """React to changes in the show_toc state."""
        toc_panel = self.query_one("#toc-panel")
        if show_toc:
            toc_panel.add_class("visible")
        else:
            toc_panel.remove_class("visible")

    def watch_show_search(self, show_search: bool) -> None:
        """React to changes in the show_search state."""
        if show_search:
            self._show_search_input()
        else:
            self._hide_search_input()

    # Event handlers
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection from the directory tree."""
        if self.file_manager.is_markdown_file(event.path):
            self._load_markdown_file(event.path)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle TOC item selection to jump to the header."""
        if event.node.data is not None:
            self._scroll_to_line(event.node.data)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self._perform_search(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in search input - go to next result."""
        if event.input.id == "search-input" and self.search_engine.search_results:
            self.search_engine.next_result()
            self._update_search_highlights()
            self._scroll_to_current_search_result()

    def on_key(self, event: Key) -> None:
        """Handle key events."""
        if self.show_search:
            if event.key == "escape":
                self.show_search = False
                event.prevent_default()
            elif event.key == "shift+enter" and self.search_engine.search_results:
                self.search_engine.previous_result()
                self._update_search_highlights()
                self._scroll_to_current_search_result()
                event.prevent_default()

    # Actions
    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

    def action_toggle_raw(self) -> None:
        """Toggle between raw and rendered markdown view."""
        self.show_raw = not self.show_raw

    def action_toggle_file_tree(self) -> None:
        """Toggle the file tree panel."""
        self.show_file_tree = not self.show_file_tree

    def action_toggle_toc(self) -> None:
        """Toggle the table of contents panel."""
        self.show_toc = not self.show_toc

    def action_toggle_search(self) -> None:
        """Toggle the search panel."""
        self.show_search = not self.show_search

    def action_export_file(self) -> None:
        """Export the markdown file to different formats."""
        if not self.markdown_content:
            self.sub_title = "No content to export"
            return
        
        # Get HTML content if in rendered mode
        html_content = None
        if not self.show_raw:
            html_content = self.markdown_processor.convert_to_html(self.markdown_content)
        
        # Export files
        base_name = self.file_manager.get_file_stem()
        export_paths = self.export_manager.export_markdown(
            self.markdown_content,
            base_name,
            html_content,
            self.show_raw
        )
        
        # Show export dialog
        self._show_export_dialog(export_paths)

    def action_open_browser(self) -> None:
        """Open the markdown in the default web browser."""
        # Check if we should open an exported file
        if self._export_html_path:
            webbrowser.open(f'file://{self._export_html_path.absolute()}')
            return
        
        # Generate HTML based on current view mode
        if self.show_raw:
            title = self.file_manager.get_filename() or APP_NAME
            html_content = self.export_manager._generate_raw_html(
                self.markdown_content, 
                title
            )
        else:
            title = self.file_manager.get_filename() or APP_NAME
            html_rendered = self.markdown_processor.convert_to_html(self.markdown_content)
            html_content = self.export_manager._generate_rendered_html(
                html_rendered,
                title
            )
        
        # Create temporary file and open in browser
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_file:
            tmp_file.write(html_content)
            tmp_file_path = tmp_file.name
        
        webbrowser.open(f'file://{tmp_file_path}')

    # Private methods
    def _load_initial_file(self, markdown_path: Path) -> None:
        """Load the initial markdown file."""
        content, last_modified = self.file_manager.load_file(markdown_path)
        self.markdown_content = content

    def _load_markdown_file(self, path: Path) -> None:
        """Load a markdown file and update the display."""
        # Stop watching the old file
        self.file_watcher.stop()
        
        # Load the new file
        content, last_modified = self.file_manager.load_file(path)
        self.markdown_content = content
        
        # Update displays
        self._update_both_views()
        self._update_header_title()
        self._build_table_of_contents()
        
        # Start watching the new file
        if last_modified is not None:  # Only watch if file loaded successfully
            self.file_watcher.start(path)
        
        # Clear search if active
        if self.show_search:
            self.search_engine.clear()
            self._perform_search("")

    def _on_file_changed(self) -> None:
        """Callback for when the watched file changes."""
        # This is called from a background thread, so use call_from_thread
        self.call_from_thread(self._reload_file)

    def _reload_file(self) -> None:
        """Reload the current file and update the display."""
        if not self.file_manager.current_file:
            return
        
        # Save current scroll position
        scroll_container = self.query_one("#content-area", VerticalScroll)
        scroll_y = scroll_container.scroll_y
        
        # Reload the file
        content, _ = self.file_manager.load_file(self.file_manager.current_file)
        
        # Only update if content actually changed
        if content != self.markdown_content:
            self.markdown_content = content
            
            # Update displays
            self._update_both_views()
            
            # Re-run search if active
            if self.search_engine.search_term:
                self._perform_search(self.search_engine.search_term)
            
            # Rebuild table of contents
            self._build_table_of_contents()
            
            # Restore scroll position
            scroll_container.scroll_to(y=scroll_y, animate=False)
            
            # Show notification
            self.sub_title = "File reloaded (auto)"
            self.set_timer(NOTIFICATION_DURATION, lambda: setattr(self, 'sub_title', ''))

    def _update_view(self) -> None:
        """Update which view is displayed based on show_raw state."""
        markdown_view = self.query_one("#markdown-view")
        raw_view = self.query_one("#raw-view")
        
        if self.show_raw:
            markdown_view.display = False
            raw_view.display = True
        else:
            self._update_markdown_view()
            markdown_view.display = True
            raw_view.display = False

    def _update_both_views(self) -> None:
        """Update both markdown and raw views with current content."""
        markdown_view = self.query_one("#markdown-view", Markdown)
        raw_view = self.query_one("#raw-view", Static)
        
        if not self.show_raw:
            processed_content = self.markdown_processor.process_with_mermaid(self.markdown_content)
            markdown_view.update(processed_content)
        else:
            markdown_view.update(self.markdown_content)
        
        raw_view.update(Text(escape(self.markdown_content)))

    def _update_markdown_view(self) -> None:
        """Update the markdown view with processed content."""
        markdown_view = self.query_one("#markdown-view", Markdown)
        processed_content = self.markdown_processor.process_with_mermaid(self.markdown_content)
        markdown_view.update(processed_content)

    def _update_header_title(self) -> None:
        """Update the header title with filename and current mode."""
        mode = "Raw" if self.show_raw else "Rendered"
        watch_status = "👁" if self.file_watcher.enabled and self.file_watcher.is_active() else ""
        
        filename = self.file_manager.get_filename()
        if filename:
            self.title = f"{APP_NAME} - {filename} [{mode}] {watch_status}"
        else:
            self.title = f"{APP_NAME} - No file loaded [{mode}]"

    def _build_table_of_contents(self) -> None:
        """Build the table of contents tree from markdown headers."""
        headers = self.markdown_processor.parse_headers(self.markdown_content)
        toc_tree = self.query_one("#toc-tree", Tree)
        self.ui_helper.build_toc_tree(toc_tree, headers)

    def _focus_content_area(self) -> None:
        """Focus the appropriate content view."""
        if self.show_raw:
            self.query_one("#raw-view", Static).focus()
        else:
            self.query_one("#markdown-view", Markdown).focus()

    def _show_search_input(self) -> None:
        """Show the search input widget."""
        search_input = Input(
            placeholder=SEARCH_PLACEHOLDER,
            id="search-input"
        )
        header = self.query_one(Header)
        self.mount(search_input, after=header)
        search_input.add_class("visible")
        search_input.focus()

    def _hide_search_input(self) -> None:
        """Hide and remove the search input widget."""
        try:
            search_input = self.query_one("#search-input", Input)
            search_input.remove()
            
            # Clear search state
            self.search_engine.clear()
            self._update_search_highlights()
            
            # Reset views to original content
            self._update_both_views()
            
            # Focus back on content
            self._focus_content_area()
        except:
            pass  # Search input doesn't exist

    def _perform_search(self, search_term: str) -> None:
        """Perform search in the current content."""
        self.search_engine.search(self.markdown_content, search_term)
        self._update_search_highlights()
        
        if self.search_engine.search_results:
            self._scroll_to_current_search_result()
        
        # Update search input placeholder with results count
        self._update_search_placeholder()

    def _update_search_highlights(self) -> None:
        """Update the display to highlight search results."""
        # Update subtitle with search status
        if self.search_engine.search_results:
            self.sub_title = self.ui_helper.generate_search_status(
                self.search_engine.search_term,
                self.search_engine.get_result_count(),
                self.search_engine.current_index + 1
            )
        elif self.search_engine.search_term:
            self.sub_title = f"Search: {self.search_engine.search_term} (no matches)"
        else:
            self.sub_title = ""
        
        # Update content display with highlights
        if self.search_engine.search_term or self.search_engine.search_results:
            if self.show_raw:
                self._update_raw_view_with_highlights()
            else:
                self._update_markdown_view_with_highlights()
        else:
            # Reset to plain content if no search
            self._update_both_views()

    def _update_raw_view_with_highlights(self) -> None:
        """Update the raw view with search highlights."""
        raw_view = self.query_one("#raw-view", Static)
        
        if not self.search_engine.search_results:
            raw_view.update(Text(escape(self.markdown_content)))
            return
        
        highlighted_text = self.ui_helper.create_highlighted_text(
            self.markdown_content,
            self.search_engine.search_results,
            self.search_engine.current_index
        )
        raw_view.update(highlighted_text)

    def _update_markdown_view_with_highlights(self) -> None:
        """Update the markdown view with search highlights."""
        markdown_view = self.query_one("#markdown-view", Markdown)
        
        if not self.search_engine.search_results:
            markdown_view.update(self.markdown_content)
            return
        
        highlighted_content = self.ui_helper.create_highlighted_markdown(
            self.markdown_content,
            self.search_engine.search_results,
            self.search_engine.current_index
        )
        
        markdown_view.update(highlighted_content)

    def _update_search_placeholder(self) -> None:
        """Update the search input placeholder with results information."""
        try:
            search_input = self.query_one("#search-input", Input)
            if self.search_engine.search_results:
                position_info = self.search_engine.get_current_position_info()
                search_input.placeholder = f"Search ({position_info} matches) - Enter: next, Shift+Enter: previous, Esc: close"
            else:
                search_input.placeholder = SEARCH_NO_MATCHES_PLACEHOLDER
        except:
            pass  # Search input doesn't exist

    def _scroll_to_line(self, line_number: int) -> None:
        """Scroll to a specific line number."""
        scroll_container = self.query_one("#content-area", VerticalScroll)
        
        try:
            viewport_height = scroll_container.size.height
            target_y = max(0, line_number - viewport_height // 3)
            scroll_container.scroll_to(y=target_y, animate=True)
        except:
            self.log(f"Would scroll to line {line_number}")

    def _scroll_to_current_search_result(self) -> None:
        """Scroll to the current search result."""
        current_result = self.search_engine.get_current_result()
        if not current_result:
            return
        
        start, _ = current_result
        line_number = self.search_engine.calculate_line_number(self.markdown_content, start)
        
        scroll_container = self.query_one("#content-area", VerticalScroll)
        
        try:
            viewport_height = scroll_container.size.height
            target_y = max(0, line_number - viewport_height // 2)
            scroll_container.scroll_to(y=target_y, animate=False)
        except:
            self.log(f"Would scroll to line {line_number}")

    def _show_export_dialog(self, export_paths) -> None:
        """Show export completion dialog."""
        # Store current state
        self._original_content = self.markdown_content
        self._original_path = self.file_manager.current_file
        
        # Display dialog content
        dialog_content = self.export_manager.generate_export_dialog_content(export_paths)
        self.markdown_content = dialog_content
        self.file_manager.current_file = None
        
        # Update views
        self._update_both_views()
        
        # Update header
        self.title = "Export Complete"
        
        # Store HTML path for opening
        self._export_html_path = export_paths.html
        
        # Restore after timeout
        self.set_timer(EXPORT_DIALOG_DURATION, self._restore_after_export)

    def _restore_after_export(self) -> None:
        """Restore original content after showing export dialog."""
        if self._original_content is not None:
            self.markdown_content = self._original_content
            self.file_manager.current_file = self._original_path
            
            # Update views
            self._update_both_views()
            
            # Update header
            self._update_header_title()
            
            # Clear temporary state
            self._export_html_path = None
            self._original_content = None
            self._original_path = None 