"""
Service for watching files for changes.
"""

import threading
import time
from pathlib import Path
from typing import Optional, Callable
from ..constants import FILE_WATCH_INTERVAL, FILE_WATCH_JOIN_TIMEOUT


class FileWatcher:
    """Handles file watching operations."""
    
    def __init__(self, callback: Callable[[], None]):
        """
        Initialize the file watcher.
        
        Args:
            callback: Function to call when file changes are detected
        """
        self.callback = callback
        self.file_path: Optional[Path] = None
        self.last_modified: Optional[float] = None
        self.watching = False
        self.watcher_thread: Optional[threading.Thread] = None
        self.enabled = True
    
    def start(self, file_path: Path) -> None:
        """
        Start watching a file for changes.
        
        Args:
            file_path: Path to the file to watch
        """
        if not file_path.exists():
            return
        
        # Stop any existing watcher
        self.stop()
        
        self.file_path = file_path
        self.last_modified = file_path.stat().st_mtime
        self.watching = True
        
        self.watcher_thread = threading.Thread(
            target=self._watch_loop,
            daemon=True
        )
        self.watcher_thread.start()
    
    def stop(self) -> None:
        """Stop watching the current file."""
        self.watching = False
        
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.watcher_thread.join(timeout=FILE_WATCH_JOIN_TIMEOUT)
        
        self.watcher_thread = None
        self.file_path = None
        self.last_modified = None
    
    def _watch_loop(self) -> None:
        """Background thread loop to watch for file changes."""
        while self.watching and self.enabled and self.file_path:
            try:
                if self.file_path.exists():
                    current_mtime = self.file_path.stat().st_mtime
                    if self.last_modified and current_mtime > self.last_modified:
                        self.last_modified = current_mtime
                        self.callback()
                
                time.sleep(FILE_WATCH_INTERVAL)
                
            except Exception as e:
                # Log error and stop watching
                print(f"File watching error: {e}")
                break
    
    def is_active(self) -> bool:
        """Check if file watching is currently active."""
        return self.watching and self.watcher_thread is not None
    
    def toggle_enabled(self) -> bool:
        """Toggle file watching on/off. Returns new enabled state."""
        self.enabled = not self.enabled
        return self.enabled 