# Klipper Terminal Console – Product Requirements Document (PRD)

## 1. Executive Summary

The Klipper Terminal Console is a terminal-native, SSH-first control and inspection tool for
Klipper-based 3D printers using Moonraker as the sole integration layer.

The product is designed for advanced users, builders, and operators who frequently manage
printers in headless or remote environments and prefer command-line workflows over web UIs.
It emphasizes discoverability, safety, and introspection while remaining extensible for
automation and community contribution.

This PRD defines the functional scope, command model, architecture, safety constraints,
and phased delivery plan for the product.

---

## 2. Problem Statement

Current Klipper interfaces (web UIs, dashboards, mobile apps) do not provide a unified,
terminal-native experience that supports:

- Fast inspection of printer state over SSH
- Macro discovery without configuration file access
- Parameter-aware command execution
- Contextual help and tab completion
- Scriptable workflows with deterministic output

Power users operating headless systems must either rely on web interfaces, manually inspect
configuration files, or issue raw G-code without guardrails or discoverability.

---

## 3. Goals and Non-Goals

### Goals
- Provide an interactive REPL-style shell over SSH
- Offer discoverable, consistent commands
- Separate read vs write actions clearly
- Use Moonraker as the single integration layer
- Remain safe when controlling physical hardware
- Support future automation and plugins without redesign

### Non-Goals
- No graphical interface
- No slicer integration
- No firmware flashing or configuration editing
- No motion planning beyond supported G-code

---

## 4. Target Personas

- Hobbyist printer builders and modders
- Advanced Klipper users running headless Linux hosts
- Developers and power users preferring CLI workflows
- Open-source contributors extending Klipper tooling

---

## 5. Default Behavior & Connectivity

### Local Defaults
- If no connection parameters are supplied:
  - Host: localhost
  - Port: 7125
  - URL: http://localhost:7125
  - Authentication: none

### Remote Connectivity
- The tool may target remote Moonraker instances
- Connection parameters may be supplied via:
  - CLI flags
  - Environment variables
  - Config file (future)

### Authentication
- Supported:
  - No authentication
  - API key authentication
- Planned:
  - Token-based authentication

If authentication is required but missing or invalid, the tool must fail clearly.

### Timeout Configuration
- Default timeout: 120 seconds
- Supports long-running operations (homing, heating, complex macros)
- Configurable via `--timeout` CLI flag
- Example: `./klipper-console.sh --timeout 180`

---

## 6. Command Philosophy & Model

### Command Naming
- list_*     → enumerate resources
- get_*      → inspect state
- set_*      → mutate state (write)
- describe   → metadata & structure
- Raw G-code → pass-through

### Design Principles
- Predictable naming
- Discoverable via tab completion
- Safe defaults
- Explicit write actions

---

## 7. Core Capabilities

### Interactive Shell
- SSH-friendly REPL
- Command history and editing
- Interrupt handling
- Persistent session context
- Graceful reconnects

### G-code Execution
- Full pass-through of Klipper-supported G-code
- Parameter validation where possible
- Real-time feedback

### Macro Support
- Enumerate macros
- Execute macros as commands
- Parameter-aware completion

### Component Support (v1)
- Fans
- Heaters
- Temperature sensors
- LEDs / neopixels
- Output pins
- Toolhead and endstops
- Macros and G-code commands

### Print Monitoring
- Real-time print status with progress tracking
- Visual progress bar display
- Timing information (print time, total time, remaining time)
- Filament usage tracking
- Print state monitoring (printing, paused, complete, etc.)

### File Management
- Local filesystem navigation (pwd, ls, cd)
- Remote directory management (mkdir, list_dir)
- File upload/download (upload_file, download_file)
- Advanced file listing with sorting and filtering
- Shell-style flags for file operations

### Console Viewer
- Interactive console mode with real-time output
- Historical message display (last 100 messages from gcode_store)
- WebSocket-based live streaming of console output
- Command execution from within console viewer
- Tab completion for G-code commands
- Color-coded message types (commands, errors, warnings, responses)
- Timestamp display for all messages
- Thread-safe message buffering with automatic truncation

---

## 8. Component Interaction Model

### Enumeration
- list_fans
- list_heaters
- list_sensors
- list_led
- list_pins
- list_macros
- list_dir - List directories on printer

### Inspection
- get_<component>
  - Lists all components of that type
- get_<component> <name>
  - Shows detailed state
- get_file [flags] [pattern]
  - Lists files with sorting and filtering
  - Flags: -t (time), -S (size), -n (name), -r (reverse)
  - Supports wildcard patterns (*.gcode)
- get_print_status
  - Shows current print job status with progress bar
  - Displays timing (print time, total time, remaining)
  - Shows filament usage and print state

### Control
- set_<component> <name> KEY=VALUE
- Write operations must be explicit

### File Operations
- **Local Navigation:**
  - pwd - Show current local directory
  - ls [flags] [pattern] - List local files
  - cd <path> - Change local directory
- **Remote Management:**
  - mkdir <path> - Create directory on printer
  - list_dir [flags] [pattern] - List printer directories
  - upload_file <local_path> [remote_path] - Upload to printer
  - download_file <remote_path> <local_path> - Download from printer
  - delete_file, move_file, copy_file - File operations
  - print_file <filename> - Start printing

### Console Operations
- **console** - Enter interactive console viewer
  - Displays historical messages from gcode_store
  - Streams real-time output via WebSocket
  - Allows command execution with tab completion
  - Press Ctrl+C to exit back to main console

---

## 9. Discoverability & Help

### Tab Completion
- **Commands** - All registered commands with inline help
- **Components** - Fan names, heater names, sensors, LEDs, pins, macros
- **Parameters** - Command-specific parameters (SPEED=, TEMP=, etc.)
- **Local Files** - Tab completion for local filesystem navigation
  - Case-insensitive matching
  - Automatic quoting for filenames with spaces
  - Directory traversal support
- **Remote Files** - Tab completion for printer files and directories
  - Case-insensitive matching
  - Automatic quoting for filenames with spaces
- **G-code Commands** - Available G-code commands from printer

### Help System
- help - List all commands with descriptions
- help <command> - Show detailed help for specific command
- Multi-line help text with proper indentation
- describe <resource> - (future) Show detailed metadata

---

## 10. Safety Model

Because the tool controls physical hardware:

- Read-only commands must be safe by default
- Write commands must be explicit
- Script mode must require confirmation for writes
- Errors must be descriptive and actionable

---

## 11. Non-Interactive / Script Mode (Future)

### Goals
- Single-command execution
- Deterministic output
- Stable exit codes
- Optional JSON output

### Exit Codes
- 0: success
- 1: general error
- 2: usage error
- 3: connection/auth error
- 4: runtime rejection

---

## 12. Architecture Overview

### Modules
- shell/
- parser/
- registry/
- moonraker/
  - client.py - HTTP client for Moonraker API
  - websocket_client.py - WebSocket client for real-time updates
- introspection/
- handlers/
- models/
- render/
- completion/
- console_viewer.py - Interactive console viewer with real-time output
- errors/

### Architectural Constraints
- Moonraker is the sole integration layer
- WebSocket runs in background thread with thread-safe message buffering
- Rendering is isolated from logic
- Handlers return structured results
- Introspection powers completion and help

---

## 13. Plugin / Extension Model (Future)

### Capabilities
- Register commands
- Provide completion providers
- Extend help and describe
- Add renderers

### Safety
- Explicit read/write declaration
- Same safety rules as core commands
- Failure isolation

---

## 14. Acceptance Criteria (MVP)

- Tool connects to Moonraker reliably
- Commands are discoverable and consistent
- get_ and set_ behavior is predictable
- Shell remains responsive
- Errors are human-readable

---

## 15. Milestone Plan

### Phase 0 – Foundation ✓ COMPLETED
- Project scaffolding
- Moonraker client
- Models

### Phase 1 – Interactive MVP ✓ COMPLETED
- REPL
- list_* and get_* commands
- G-code pass-through

### Phase 2 – Control & Discoverability ✓ COMPLETED
- set_* commands
- help and describe
- Advanced completion
- Tab completion for components and parameters

### Phase 3 – File Management ✓ COMPLETED
- Local filesystem navigation (pwd, ls, cd)
- Remote directory management (mkdir, list_dir)
- File upload/download
- Advanced file listing with shell-style flags
- Case-insensitive tab completion
- Quoted filename support for files with spaces

### Phase 4 – Console Viewer ✓ COMPLETED
- Interactive console mode with real-time output
- Historical message display from gcode_store
- WebSocket integration for live streaming
- Command execution from console viewer
- Tab completion for G-code commands
- Color-coded message types
- Thread-safe message buffering

### Phase 5 – Stability & Optimization ✓ COMPLETED
- Timeout configuration (120s default for long-running operations)
- Error handling improvements
- Output spacing and formatting
- Performance optimization

### Phase 6 – v1.0 (PLANNED)
- Comprehensive documentation
- User guide and tutorials
- Stable release

---

## 16. Licensing

MIT License
