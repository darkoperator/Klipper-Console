# Changelog

All notable changes to Klipper Console will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Moonraker update_manager support for automatic updates via Mainsail/Fluidd
- Installation script (scripts/install.sh) for automated setup
- Update manager configuration template (scripts/klipper-console-moonraker.conf)
- Quick copy-paste configuration snippet (scripts/moonraker-update-snippet.txt)
- GitHub release workflow for automated releases
- Comprehensive installation documentation (docs/user-guide/INSTALLATION.md)
- Method 4 installation instructions in README.md
- Initial public release preparation
- Comprehensive README with installation instructions
- CONTRIBUTING.md with development guidelines
- MIT License

## [0.1.0] - 2025-01-26

### Added
- Interactive REPL with command history and auto-suggestions
- Smart context-aware tab completion
- Component inspection commands (get_sensor, get_fan, get_heater, etc.)
- Component control commands (set_fan, set_led, set_heater, etc.)
- File management with local navigation (pwd, ls, cd)
- Remote file operations (upload_file, download_file, mkdir)
- Advanced file listing with shell-style flags (-t, -S, -r, -a)
- Wildcard pattern support for file filtering
- Print monitoring with progress bar and timing
- Macro execution with parameter support
- Motion control (home, extrude)
- Interactive console viewer with real-time output
- WebSocket integration for live console streaming
- Historical message display from gcode_store
- Color-coded console output
- G-code command tab completion in console mode
- Thread-safe message buffering

### Changed
- Increased default timeout from 10s to 120s for long-running operations
- Improved output spacing and formatting

### Fixed
- Timeout errors on operations like homing
- Output buffering issues

### Infrastructure
- Python 3.10+ support
- Dependencies: prompt_toolkit, httpx, rich, websocket-client
- Modular architecture with separated concerns
- Comprehensive error handling
- Type hints throughout codebase

## [0.0.1] - 2025-01-15

### Added
- Initial project scaffolding
- Basic Moonraker client
- Core data models
- Command parsing and registry
- Basic REPL shell

[Unreleased]: https://github.com/darkoperator/Klipper-Console/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/darkoperator/Klipper-Console/releases/tag/v0.1.0
[0.0.1]: https://github.com/darkoperator/Klipper-Console/releases/tag/v0.0.1
