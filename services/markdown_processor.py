"""
Service for processing markdown content.
"""

import re
from typing import List, Optional
from markdown import markdown
from app_types import MermaidBlock, Header, MermaidBlockList, HeaderList
from constants import MERMAID_PREVIEW_LINES, MERMAID_PREVIEW_MAX_LENGTH


class MarkdownProcessor:
    """Handles markdown processing operations."""
    
    def __init__(self):
        self.mermaid_blocks: MermaidBlockList = []
    
    def detect_mermaid_blocks(self, content: str) -> MermaidBlockList:
        """
        Detect Mermaid diagram blocks in the markdown content.
        
        Args:
            content: The markdown content to process
            
        Returns:
            List of MermaidBlock objects
        """
        mermaid_blocks = []
        lines = content.split('\n')
        in_mermaid_block = False
        block_start = -1
        block_content = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```mermaid'):
                in_mermaid_block = True
                block_start = i
                block_content = []
            elif in_mermaid_block and line.strip() == '```':
                in_mermaid_block = False
                mermaid_blocks.append(MermaidBlock(
                    start_line=block_start,
                    end_line=i,
                    content='\n'.join(block_content)
                ))
            elif in_mermaid_block:
                block_content.append(line)
        
        self.mermaid_blocks = mermaid_blocks
        return mermaid_blocks
    
    def process_with_mermaid(self, content: str) -> str:
        """
        Process markdown content to handle Mermaid diagrams.
        
        Args:
            content: The markdown content to process
            
        Returns:
            Processed markdown with Mermaid placeholders
        """
        self.detect_mermaid_blocks(content)
        
        if not self.mermaid_blocks:
            return self.fix_bullet_lists(content)
        
        lines = content.split('\n')
        processed_lines = []
        current_line = 0
        
        for block in self.mermaid_blocks:
            # Add lines before the Mermaid block
            processed_lines.extend(lines[current_line:block.start_line])
            
            # Add a placeholder for the Mermaid diagram
            processed_lines.append('```')
            processed_lines.append('╔══════════════════════════════════════╗')
            processed_lines.append('║        MERMAID DIAGRAM               ║')
            processed_lines.append('║                                      ║')
            processed_lines.append('║  [View in browser with "o" key]      ║')
            processed_lines.append('║                                      ║')
            
            # Add a preview of the Mermaid content
            preview_lines = block.content.strip().split('\n')[:MERMAID_PREVIEW_LINES]
            for line in preview_lines:
                if len(line) > MERMAID_PREVIEW_MAX_LENGTH:
                    line = line[:MERMAID_PREVIEW_MAX_LENGTH - 3] + '...'
                processed_lines.append(f'║  {line:<36} ║')
            
            if len(preview_lines) < len(block.content.strip().split('\n')):
                processed_lines.append('║  ...                                 ║')
            
            processed_lines.append('╚══════════════════════════════════════╝')
            processed_lines.append('```')
            
            current_line = block.end_line + 1
        
        # Add remaining lines
        processed_lines.extend(lines[current_line:])
        
        result = '\n'.join(processed_lines)
        return self.fix_bullet_lists(result)
    
    def fix_bullet_lists(self, content: str) -> str:
        """
        Placeholder for bullet list rendering fix.
        
        NOTE: There is a known issue with Textual's Markdown widget (v5.0.1) where
        bullet points and their text are rendered on separate lines. This is a 
        limitation of the widget itself and cannot be fixed with text preprocessing
        or CSS alone.
        
        Args:
            content: The markdown content
            
        Returns:
            The content unchanged
        """
        return content
    
    def parse_headers(self, content: str) -> HeaderList:
        """
        Parse markdown content to extract headers.
        
        Args:
            content: The markdown content to parse
            
        Returns:
            List of Header objects
        """
        headers = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines):
            # Check for ATX-style headers (# Header)
            match = re.match(r'^(#{1,6})\s+(.+)', line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headers.append(Header(
                    level=level,
                    title=title,
                    line_number=line_num
                ))
        
        return headers
    
    def convert_to_html(self, content: str) -> str:
        """
        Convert markdown to HTML with Mermaid diagram support.
        
        Args:
            content: The markdown content to convert
            
        Returns:
            HTML string
        """
        self.detect_mermaid_blocks(content)
        
        if not self.mermaid_blocks:
            # No Mermaid blocks, just convert normally
            return markdown(content)
        
        # Process markdown with Mermaid blocks
        lines = content.split('\n')
        processed_lines = []
        current_line = 0
        
        for block in self.mermaid_blocks:
            # Add lines before the Mermaid block
            processed_lines.extend(lines[current_line:block.start_line])
            
            # Add Mermaid div
            processed_lines.append(f'<div class="mermaid">')
            processed_lines.append(block.content)
            processed_lines.append('</div>')
            
            current_line = block.end_line + 1
        
        # Add remaining lines
        processed_lines.extend(lines[current_line:])
        
        # Convert the processed markdown to HTML
        processed_markdown = '\n'.join(processed_lines)
        return markdown(processed_markdown) 