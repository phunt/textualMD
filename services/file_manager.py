"""
Service for handling file operations.
"""

from pathlib import Path
from typing import Optional, Tuple
from constants import MARKDOWN_EXTENSIONS, ERROR_CONTENT_TEMPLATE


class FileManager:
    """Handles file-related operations."""
    
    def __init__(self):
        self.current_file: Optional[Path] = None
        self.current_content: str = ""
    
    def load_file(self, file_path: Path) -> Tuple[str, Optional[float]]:
        """
        Load a markdown file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Tuple of (content, last_modified_time) or (error_content, None)
        """
        try:
            if not file_path.exists():
                error_msg = ERROR_CONTENT_TEMPLATE.format(
                    message=f"File not found: {file_path}"
                )
                return error_msg, None
            
            content = file_path.read_text(encoding='utf-8')
            last_modified = file_path.stat().st_mtime
            
            self.current_file = file_path
            self.current_content = content
            
            return content, last_modified
            
        except Exception as e:
            error_msg = ERROR_CONTENT_TEMPLATE.format(
                message=f"Could not read file: {file_path}\n\nError: {str(e)}"
            )
            return error_msg, None
    
    def is_markdown_file(self, file_path: Path) -> bool:
        """
        Check if a file is a markdown file based on its extension.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if the file has a markdown extension
        """
        return file_path.suffix.lower() in MARKDOWN_EXTENSIONS
    
    def get_filename(self) -> str:
        """
        Get the current filename.
        
        Returns:
            Filename or empty string if no file is loaded
        """
        if self.current_file:
            return self.current_file.name
        return ""
    
    def get_file_stem(self) -> str:
        """
        Get the current file stem (name without extension).
        
        Returns:
            File stem or 'markdown_export' as default
        """
        if self.current_file:
            return self.current_file.stem
        return "markdown_export"
    
    def get_absolute_path(self) -> Optional[Path]:
        """
        Get the absolute path of the current file.
        
        Returns:
            Absolute path or None if no file is loaded
        """
        if self.current_file:
            return self.current_file.absolute()
        return None 