"""
Type definitions and data classes for the Markdown Viewer application.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path


@dataclass
class MermaidBlock:
    """Represents a Mermaid diagram block in markdown."""
    start_line: int
    end_line: int
    content: str


@dataclass
class Header:
    """Represents a markdown header."""
    level: int
    title: str
    line_number: int


@dataclass
class SearchResult:
    """Represents a search result in the document."""
    start: int
    end: int
    line_number: int
    match_text: str


@dataclass
class ExportPaths:
    """Paths for exported files."""
    html: Path
    text: Path


# Type aliases
SearchResults = List[Tuple[int, int]]
HeaderList = List[Header]
MermaidBlockList = List[MermaidBlock] 