"""
Service for handling search functionality within markdown documents.
"""

import re
from typing import List, Tuple, Optional
from app_types import SearchResults


class SearchEngine:
    """Handles search operations within markdown content."""
    
    def __init__(self):
        self.search_results: SearchResults = []
        self.current_index = 0
        self.search_term = ""
    
    def search(self, content: str, search_term: str) -> SearchResults:
        """
        Perform a case-insensitive search in the content.
        
        Args:
            content: The text content to search in
            search_term: The term to search for
            
        Returns:
            List of (start, end) tuples for match positions
        """
        if not search_term:
            self.search_results = []
            self.current_index = 0
            self.search_term = ""
            return []
        
        self.search_term = search_term
        pattern = re.escape(search_term)
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        
        self.search_results = [(m.start(), m.end()) for m in matches]
        self.current_index = 0 if self.search_results else -1
        
        return self.search_results
    
    def next_result(self) -> Optional[int]:
        """
        Move to the next search result.
        
        Returns:
            The new current index, or None if no results
        """
        if not self.search_results:
            return None
        
        self.current_index = (self.current_index + 1) % len(self.search_results)
        return self.current_index
    
    def previous_result(self) -> Optional[int]:
        """
        Move to the previous search result.
        
        Returns:
            The new current index, or None if no results
        """
        if not self.search_results:
            return None
        
        self.current_index = (self.current_index - 1) % len(self.search_results)
        return self.current_index
    
    def get_current_result(self) -> Optional[Tuple[int, int]]:
        """
        Get the current search result position.
        
        Returns:
            (start, end) tuple of the current match, or None
        """
        if not self.search_results or self.current_index < 0:
            return None
        
        return self.search_results[self.current_index]
    
    def get_result_count(self) -> int:
        """Get the total number of search results."""
        return len(self.search_results)
    
    def get_current_position_info(self) -> str:
        """
        Get a string describing the current search position.
        
        Returns:
            String like "3/10" for result 3 of 10
        """
        if not self.search_results:
            return "0/0"
        
        return f"{self.current_index + 1}/{len(self.search_results)}"
    
    def clear(self) -> None:
        """Clear all search results."""
        self.search_results = []
        self.current_index = 0
        self.search_term = ""
    
    def calculate_line_number(self, content: str, position: int) -> int:
        """
        Calculate the line number for a given position in the content.
        
        Args:
            content: The text content
            position: Character position in the content
            
        Returns:
            Zero-based line number
        """
        return content[:position].count('\n') 