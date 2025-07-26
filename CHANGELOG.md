# Changelog

All notable changes to TextualMD will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-17

### Added
- Proper Python package structure using `src/` layout
- `pyproject.toml` for modern Python packaging
- Global installation support via `uv tool install`
- Two command-line entry points: `textualmd` and `tmd` (shorter alias)
- Comprehensive development documentation

### Changed
- Migrated from simple script to proper Python package
- Restructured code into `src/textualmd/` directory
- Updated all imports to use relative imports
- Replaced `requirements.txt` with `pyproject.toml` (kept for legacy)
- Updated documentation to reflect new installation and usage

### Technical Details
- Now requires Python 3.13+ (configurable in pyproject.toml)
- Uses Hatchling as build backend
- Fully compatible with uv package manager
- Supports both global installation and development mode 