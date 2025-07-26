"""
UI widgets and helper functions for the Markdown Viewer application.
"""

from textual.widgets import Tree
from typing import List, Optional
from rich.text import Text
from rich.markup import escape
from ..app_types import HeaderList, SearchResults


class UIHelper:
    """Helper class for UI-related operations."""
    
    @staticmethod
    def build_toc_tree(tree: Tree, headers: HeaderList) -> None:
        """
        Build a table of contents tree from headers.
        
        Args:
            tree: The Tree widget to populate
            headers: List of Header objects
        """
        tree.clear()
        
        if not headers:
            tree.root.add_leaf("No headers found")
            return
        
        # Build tree structure based on header levels
        node_stack = [(0, tree.root)]  # (level, node)
        
        for header in headers:
            level = header.level
            title = header.title
            line = header.line_number
            
            # Find the appropriate parent node
            while node_stack and node_stack[-1][0] >= level:
                node_stack.pop()
            
            # Add the new node
            parent_node = node_stack[-1][1] if node_stack else tree.root
            new_node = parent_node.add(title, data=line)
            
            # Add to stack for potential children
            node_stack.append((level, new_node))
        
        # Expand the root to show the TOC
        tree.root.expand()
    
    @staticmethod
    def create_highlighted_text(
        content: str, 
        search_results: SearchResults, 
        current_index: int
    ) -> Text:
        """
        Create a Rich Text object with search highlights.
        
        Args:
            content: The text content
            search_results: List of (start, end) tuples
            current_index: Index of the current search result
            
        Returns:
            Rich Text object with highlighting
        """
        # Create a Rich Text object with the escaped content
        text = Text(escape(content))
        
        # Apply highlighting to all matches
        for i, (start, end) in enumerate(search_results):
            if i == current_index:
                # Current match - use orange background
                text.stylize("bold yellow on dark_orange", start, end)
            else:
                # Other matches - use yellow background
                text.stylize("black on yellow", start, end)
        
        return text
    
    @staticmethod
    def create_highlighted_markdown(
        content: str,
        search_results: SearchResults,
        current_index: int
    ) -> str:
        """
        Create markdown content with search highlights using unicode markers.
        
        Args:
            content: The markdown content
            search_results: List of (start, end) tuples
            current_index: Index of the current search result
            
        Returns:
            Markdown string with unicode highlight markers
        """
        if not search_results:
            return content
        
        highlighted_content = content
        
        # Sort results by position in reverse order to avoid offset issues
        sorted_results = sorted(
            enumerate(search_results), 
            key=lambda x: x[1][0], 
            reverse=True
        )
        
        # Apply visual highlighting with unicode characters
        for i, (start, end) in sorted_results:
            match_text = highlighted_content[start:end]
            
            if i == current_index:
                # Current match - use distinctive markers
                replacement = f'【{match_text}】'
            else:
                # Other matches - use lighter markers
                replacement = f'〖{match_text}〗'
            
            highlighted_content = (
                highlighted_content[:start] + 
                replacement + 
                highlighted_content[end:]
            )
        
        return highlighted_content
    
    @staticmethod
    def generate_search_status(
        search_term: str,
        result_count: int,
        current_position: int
    ) -> str:
        """
        Generate a search status string.
        
        Args:
            search_term: The current search term
            result_count: Total number of results
            current_position: Current result position (1-indexed)
            
        Returns:
            Status string for display
        """
        if result_count > 0:
            return f"Search: {search_term} ({current_position}/{result_count})"
        elif search_term:
            return f"Search: {search_term} (no matches)"
        else:
            return "" 