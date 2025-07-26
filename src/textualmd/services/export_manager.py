"""
Service for handling export functionality.
"""

import time
from pathlib import Path
from typing import Optional
from ..app_types import ExportPaths
from ..constants import (
    EXPORT_DIR_NAME, 
    EXPORT_TIMESTAMP_FORMAT, 
    HTML_STYLE, 
    RAW_HTML_STYLE
)


class ExportManager:
    """Handles exporting markdown to various formats."""
    
    def __init__(self):
        self.export_dir = Path(EXPORT_DIR_NAME)
    
    def ensure_export_directory(self) -> Path:
        """
        Ensure the export directory exists.
        
        Returns:
            Path to the export directory
        """
        self.export_dir.mkdir(exist_ok=True)
        return self.export_dir
    
    def generate_export_filename(self, base_name: str, extension: str) -> Path:
        """
        Generate a timestamped export filename.
        
        Args:
            base_name: Base name for the file
            extension: File extension (without dot)
            
        Returns:
            Path object for the export file
        """
        timestamp = time.strftime(EXPORT_TIMESTAMP_FORMAT)
        filename = f"{base_name}_{timestamp}.{extension}"
        return self.export_dir / filename
    
    def export_as_html(
        self, 
        content: str, 
        title: str, 
        output_path: Path,
        html_content: Optional[str] = None,
        is_raw: bool = False
    ) -> None:
        """
        Export content as HTML file.
        
        Args:
            content: The markdown content (for raw view)
            title: Document title
            output_path: Path to save the HTML file
            html_content: Pre-rendered HTML content (if available)
            is_raw: Whether to export as raw markdown
        """
        if is_raw:
            html_document = self._generate_raw_html(content, title)
        else:
            if not html_content:
                from markdown import markdown
                html_content = markdown(content)
            html_document = self._generate_rendered_html(html_content, title)
        
        output_path.write_text(html_document, encoding='utf-8')
    
    def export_as_text(self, content: str, output_path: Path) -> None:
        """
        Export content as plain text file.
        
        Args:
            content: The text content to export
            output_path: Path to save the text file
        """
        output_path.write_text(content, encoding='utf-8')
    
    def export_markdown(
        self, 
        content: str, 
        base_name: str,
        html_content: Optional[str] = None,
        is_raw: bool = False
    ) -> ExportPaths:
        """
        Export markdown to multiple formats.
        
        Args:
            content: The markdown content
            base_name: Base filename for exports
            html_content: Pre-rendered HTML content (if available)
            is_raw: Whether to export as raw markdown
            
        Returns:
            ExportPaths object with paths to exported files
        """
        self.ensure_export_directory()
        
        # Generate filenames
        html_path = self.generate_export_filename(base_name, 'html')
        text_path = self.generate_export_filename(base_name, 'txt')
        
        # Export files
        self.export_as_html(content, base_name, html_path, html_content, is_raw)
        self.export_as_text(content, text_path)
        
        return ExportPaths(html=html_path, text=text_path)
    
    def _generate_raw_html(self, content: str, title: str) -> str:
        """Generate HTML for raw markdown view."""
        # Escape HTML entities
        from html import escape
        escaped_content = escape(content)
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} (Raw)</title>
    <style>
{RAW_HTML_STYLE}
    </style>
</head>
<body>
    <pre>{escaped_content}</pre>
</body>
</html>"""
    
    def _generate_rendered_html(self, html_content: str, title: str) -> str:
        """Generate HTML for rendered markdown view."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    <style>
{HTML_STYLE}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
    
    def generate_export_dialog_content(self, export_paths: ExportPaths) -> str:
        """
        Generate markdown content for the export completion dialog.
        
        Args:
            export_paths: Paths to the exported files
            
        Returns:
            Markdown string for the dialog
        """
        return f"""# Export Complete! 

Files have been exported to the '{EXPORT_DIR_NAME}' directory:

## Exported Files:
- **HTML**: `{export_paths.html.name}`
- **Text**: `{export_paths.text.name}`

## To Create PDF:
1. Open the HTML file in your browser
2. Press Ctrl/Cmd + P to print
3. Select "Save as PDF" as the printer
4. Click Save

## To Create DOCX:
1. Open the HTML file in your browser
2. Select all content (Ctrl/Cmd + A)
3. Copy (Ctrl/Cmd + C)
4. Paste into Microsoft Word or Google Docs
5. Save as DOCX

Press 'o' to open the HTML file in your browser now!
""" 