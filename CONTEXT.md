# TextualMD Project Context

TextualMD is a terminal-based Markdown viewer built with the Textual framework, designed to provide a rich, interactive experience for viewing and working with Markdown files directly in the terminal.

## Project Overview

### Purpose
A powerful, feature-rich terminal application that allows users to:
- View rendered Markdown with syntax highlighting and formatting
- Navigate documents with table of contents
- Search within documents
- Export to multiple formats (HTML, PDF, DOCX)
- Browse and open files through an integrated file explorer

### Key Technologies
- **Python 3.13+**: Modern Python for type hints and performance
- **Textual 5.0.1**: Terminal UI framework for rich interfaces
- **Markdown 3.8.2**: Markdown to HTML conversion
- **uv**: Fast Python package manager for dependency management

## Architecture

### Package Structure
The project follows a standard Python package layout:
- `src/textualmd/`: Main package directory
  - `app.py`: Core application class and logic
  - `main.py`: Entry point and CLI handling
  - `constants.py`: Application-wide constants
  - `app_types.py`: Type definitions and data classes
  - `services/`: Business logic services
  - `ui/`: User interface components

### Key Components

1. **MarkdownViewerApp** (app.py)
   - Main application class inheriting from Textual's App
   - Manages UI state, file operations, and user interactions
   - Coordinates between services and UI components

2. **Services Layer**
   - `FileManager`: Handles file I/O operations
   - `FileWatcher`: Monitors files for changes
   - `MarkdownProcessor`: Processes Markdown content, extracts headers and Mermaid blocks
   - `SearchEngine`: Implements search functionality
   - `ExportManager`: Handles export to various formats

3. **UI Layer**
   - `styles.py`: CSS styling for the application
   - `bindings.py`: Keyboard shortcut definitions
   - `widgets.py`: Custom UI components and helpers

### Design Decisions

1. **Service-Oriented Architecture**: Business logic is separated into focused service classes for maintainability

2. **Reactive UI**: Uses Textual's reactive programming model for responsive interfaces

3. **Type Safety**: Extensive use of Python type hints and custom types for reliability

4. **Modular Structure**: Clear separation between UI, business logic, and data types

## Development Workflow

The project uses `uv` for package management, providing:
- Fast dependency resolution
- Reproducible builds with `uv.lock`
- Simple global installation with `uv tool install`
- Development mode with editable installs

## Future Considerations

- Plugin system for extensibility
- Performance optimization for large documents
- Enhanced Markdown extensions support
- Collaborative features
- AI-powered enhancements

See `TODO.md` for the complete roadmap of planned features.
