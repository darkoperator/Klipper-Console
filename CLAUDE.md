# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Klipper Terminal Console is a terminal-native, SSH-first REPL for controlling Klipper-based 3D printers via Moonraker. It provides discoverable commands with tab completion, strong safety semantics (explicit read vs write), and is designed for headless/remote printer management.

## Development Commands

### Install for development
```bash
python3 -m venv venv
./venv/bin/pip install -e .
```

### Run the console
```bash
./venv/bin/klipper-console
# or use the wrapper script:
./klipper-console.sh
```

The console defaults to `http://localhost:7125` with no authentication.

## Architecture

### Core Design Principles

1. **Moonraker is the sole integration layer** - all printer communication goes through Moonraker HTTP API
2. **Separation of concerns**:
   - `parser/` - command parsing
   - `registry/` - command registration and routing
   - `handlers/` - command execution logic
   - `moonraker/client.py` - HTTP client with auth support
   - `shell.py` - REPL loop using prompt_toolkit
   - `render/` - output formatting (isolated from logic)
   - `introspection/` - powers tab completion and help system
   - `completion/` - tab completion providers
   - `models/` - data models for printer components
   - `errors.py` - error handling and mapping

3. **Handlers return structured results** - rendering is separated from business logic

### Command Model

Commands follow strict naming conventions:
- `get_*` - inspect state (read-only)
  - Without arguments: returns all items (e.g., `get_sensor` returns all sensors)
  - With name argument: returns specific item (e.g., `get_sensor chamber`)
- `set_*` - mutate state (write operations, must be explicit)
- Raw G-code - pass-through to Klipper (future)

### Safety Model

Physical hardware control requires explicit semantics:
- Read-only commands (`list_*`, `get_*`) must be safe by default
- Write commands (`set_*`) must be explicit and clearly named
- Script mode (future) requires confirmation for write operations
- Errors must be descriptive and actionable

### Component Support (Phase 1)

Initial component types:
- Fans
- Heaters
- Temperature sensors
- LEDs / neopixels
- Macros (discoverable and executable)

## Entry Point

CLI entry point is defined in `pyproject.toml`:
```toml
[project.scripts]
klipper-console = "klipper_console.cli:main"
```

The `cli.py` module handles argument parsing and connection parameters, then starts the shell.

## Authentication

Supported modes:
- No authentication (default for localhost)
- API key authentication
- Token-based auth (planned)

Connection parameters can be supplied via CLI flags or environment variables.

## Dependencies

Core libraries:
- `prompt_toolkit>=3.0` - REPL interface, line editing, history
- `httpx>=0.27` - async HTTP client for Moonraker
- `rich>=13.7` - terminal rendering and formatting

## Tab Completion

The console includes context-aware tab completion in `completion/__init__.py`:

- **Command completion**: Completes command names
- **Component name completion**: Dynamically fetches and caches component names from Moonraker
  - Typing `get_sensor <Tab>` shows all available sensors
  - Typing `get_sensor ch<Tab>` filters to sensors starting with "ch"
- **Parameter completion**: Completes parameter names for set commands
  - `set_fan BedFans S<Tab>` → `SPEED=`
  - `set_led sb_leds R<Tab>` → `RED=`

The completer caches component lists on first use to minimize API calls.

## Milestone Context

The project has completed **Phase 1** (Interactive MVP):
- ✅ REPL with prompt_toolkit
- ✅ Basic commands (`get_*`, `set_*`)
- ✅ Context-aware tab completion
- ✅ Rich formatted output
- ✅ Tested with live printer

Next phases will add:
- G-code pass-through
- Advanced help/describe system
- Plugin/extension support

When implementing features, refer to PRD.md for detailed requirements and phase definitions.
